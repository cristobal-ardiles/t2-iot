import sys 
sys.path += ["/home/cristobal/.local/lib/python3.10/site-packages",
             "/home/cristobal/.local/lib/python3.10/site-packages/gattlib-0.20210616-py3.10-linux-x86_64.egg"]
print(sys.path)
import pygatt
import DatabaseWork as db
import Desempaquetamiento as des
import keyboard
from datetime import datetime
from gattlib import GATTRequester, GATTResponse
import time

# Definir los UUIDs de los servicios y características del dispositivo BLE
DEVICE_ADDRESS = '4C:EB:D6:61:FE:D6'
SERVICE_UUID = '0000fff0-0000-1000-8000-00805f9b34fb' # ID del servicio
CHARACTERISTIC_UUID_CONFIG = '0000ff01-0000-1000-8000-00805f9b34fb' # ID de la caracteristica del servicio
CHARACTERISTIC_UUID_DATA = '0000ee01-0000-1000-8000-00805f9b34fb'
CHARACTERISTIC_HANDLE_CONFIG = 0x2a
CHARACTERISTIC_HANDLE_DATA = 0X2e
# Inicializar la conexión PyGatt
# adapter = pygatt.GATTToolBackend()

# Global variables
attempts = 0
device = None # Dispositivo BLE
status = 10 # Estado de la comunicacion
subscribed = False


class Requester(GATTRequester):
    def on_notification(self, handle, data):
        handle_notification(handle, data)
    def on_indication(self, handle, data):
        handle_notification(handle, data)

req = None

# Subscribe, cada vez que el esp32 cambie la caracteristica notificara a la raspberry
# Envia un send indicate

# Nosotros ocupamos un write para mandar un mensaje al esp32 indicando la configuracion
# El nos manda la notificacion con el mensaje que le pedimos y hacemos el read
# Leemos la caracteristica asociada a la notificacion para obtener los valores nuevos.
# Detener el envio de datos, leer el valor de la config y si yo no la he cambiado es porque todavia no he recibido los datos.

ASYNC = False
req = Requester(DEVICE_ADDRESS)
def read_data():
    global ASYNC
    if ASYNC:
        response = GATTResponse()
        
        print("Trying to read")
    
        req.read_by_handle_async(CHARACTERISTIC_HANDLE_DATA, response)

        # Busy waiting
        while not response.received():
            time.sleep(0.1)
        
        ret = response.received()[0]
        
    else:
        while True: 
            try:
                ret = req.read_by_uuid(CHARACTERISTIC_UUID_DATA)[0]
                break
            except: 
                write_config()
                print("Failed")
    return ret

# Conectar al dispositivo BLE

def connect():
    """Conectar al dispositivo BLE. Intenta hasta que logra conectarse.
    Una vez conectado, envia la configuracion de la comunicacion y se suscribe a la caracteristica de notificacion"""
    # adapter.start()
    ts = datetime.now()
    while True:
        try:
            global attempts
            attempts += 1
            print("Intento: ", attempts)
            # Intentamos conectar con el dispositivo
            global req
            # device = adapter.connect(DEVICE_ADDRESS, timeout=1, auto_reconnect=False) # auto_reconnect=True
            print("Conectado")
            config = read_data()
            print(config)
            header = des.getHeader(config)
            data = {'Timestamp':ts}
            # Guardamos en la BD la cantidad de intentos y el tiempo de conexion
            db.lossSave(header, data, attempts)
            print("Loss guardada")
            break
        except pygatt.exceptions.BLEError:
            print("Error al conectar con el dispositivo")
            # Volvemos a intentar
            continue
        ## Una vez conectado, nos subscribimos a la caracteristica de notificacion
        #device.subscribe(CHARACTERISTIC_UUID_DATA, callback=handle_notification) # Observamos la caracteristica
        
        ## MAC(0,5), TIMESTAMP(6,9), STATUS(10) 

def handle_notification(handle, value):
    """Funcion para manejar notificaciones de caracteristicas. Al recibir una notificacion, se lee la caracteristica asociada a la notificacion, 
    se parsea la data, se guarda en la bdd y se printea el contenido de esta."""
    print("Notificacion recibida: ", value.hex())
    # ACA DEBERIAMOS HACER EL READ DE LAS COSAS, PARSEARLAS, Y MANDARLAS A LA BASE DE DATOS
    # Una vez llegada la notificacion, debemos leer la caracteristica
    #data = device.char_read_handle(handle)
    # Leemos la caracteristica asociada a la notificacion
    try: 
        data = read_data()
        response_dict = des.parseData(data) # Parsea la data, la devuelve en un diccionario. Guarda la informacion en la base de datos
        print("Data parseada: ", response_dict)
    except pygatt.exceptions.NotificationTimeout:
        try:
            data = read_data()
            response_dict = des.parseData(data) # Parsea la data, la devuelve en un diccionario. Guarda la informacion en la base de datos
            print("Data parseada: ", response_dict)
        except pygatt.exceptions.NotificationTimeout:
            print("No leyó")
    # Parseamos la data

def disconnect():
    """Desconectar del dispositivo BLE"""
    global status
    global subscribed
    global attempts
    # Damos aviso de que nos desconectamos
    print("Desconectando del dispositivo")
    status = 10
    subscribed = False
    attempts = 0
    write_config() # Configuracion de la comunicacion
    # adapter.stop()


def subscribe_device(status):
    try:
        device.subscribe(CHARACTERISTIC_UUID_DATA, 
                            callback=handle_notification, 
                            indication = True if status == 31 else False,
                            wait_for_response = True)
    except:
        print("Response not received")
# Main loop

def write_config():
    payload = bytes([status, protocol])
    print(f"Writing config: status={status}, protocol={protocol}")
    req.write_by_handle(CHARACTERISTIC_HANDLE_CONFIG, payload)
while True:

    if status == 10:
        connect()
        # Una vez conectado, enviamos la configuracion de la comunicacion
        protocol, status = db.getConfig()

    write_config()# Configuracion de la comunicacion
    
    # Esperar la data
    while True: 
        if keyboard.is_pressed('esc'):
            disconnect()
            break
        elif keyboard.is_pressed('s'):
            status = 30 if status == 31 else 31
            db.save_config(status, protocol)
            disconnect()
            break
        elif keyboard.is_pressed('p'):
            protocol = (protocol + 1) % 4
            db.save_config(status, protocol)
            disconnect()
            break