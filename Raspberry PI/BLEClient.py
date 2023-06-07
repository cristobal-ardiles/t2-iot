import pygatt
import DatabaseWork as db
import Desempaquetamiento as des

# Definir los UUIDs de los servicios y características del dispositivo BLE
DEVICE_ADDRESS = '4C:EB:D6:61:FE:D6'
SERVICE_UUID = '0000fff0-0000-1000-8000-00805f9b34fb' # ID del servicio
CHARACTERISTIC_UUID_CONFIG = '0000fff1-0000-1000-8000-00805f9b34fb' # ID de la caracteristica del servicio
CHARACTERISTIC_UUID_DATA = '0000fff1-0000-1000-8000-00805f9b34fb'

# Inicializar la conexión PyGatt
adapter = pygatt.GATTToolBackend()

# Global variables
attempts = 0
device = None # Dispositivo BLE

# Subscribe, cada vez que el esp32 cambie la caracteristica notificara a la raspberry
# Envia un send indicate

# Nosotros ocupamos un write para mandar un mensaje al esp32 indicando la configuracion
# El nos manda la notificacion con el mensaje que le pedimos y hacemos el read
# Leemos la caracteristica asociada a la notificacion para obtener los valores nuevos.
# Detener el envio de datos, leer el valor de la config y si yo no la he cambiado es porque todavia no he recibido los datos.


# Conectar al dispositivo BLE
def connect():
    """Conectar al dispositivo BLE. Intenta hasta que logra conectarse.
    Una vez conectado, envia la configuracion de la comunicacion y se suscribe a la caracteristica de notificacion"""
    while True:
        try:
            print("Intento: ", attempts)
            # Intentamos conectar con el dispositivo
            global device
            device = adapter.connect(DEVICE_ADDRESS, address_type=pygatt.BLEAddressType.random, timeout=10, auto_reconnect=False) # auto_reconnect=True
            device.subscribe(CHARACTERISTIC_UUID_DATA, callback=handle_notification) # Observamos la caracteristica
        except pygatt.exceptions.BLEError:
            print("Error al conectar con el dispositivo")
            # Volvemos a intentar
            continue

def handle_notification(handle, value):
    """Funcion para manejar notificaciones de caracteristicas. Al recibir una notificacion, se lee la caracteristica asociada a la notificacion, 
    se parsea la data, se guarda en la bdd y se printea el contenido de esta."""
    print("Notificacion recibida: ", value.hex())
    # ACA DEBERIAMOS HACER EL READ DE LAS COSAS, PARSEARLAS, Y MANDARLAS A LA BASE DE DATOS
    # Una vez llegada la notificacion, debemos leer la caracteristica
    data = device.char_read_handle(handle)
    # Parseamos la data
    response_dict = des.parseData(data) # Parsea la data, la devuelve en un diccionario. Guarda la informacion en la base de datos
    print("Data parseada: ", response_dict)

def disconnect():
    """Desconectar del dispositivo BLE"""
    adapter.stop()


# Main loop

while True:
    try:
        # Intentamos conectar con el dispositivo
        attempts += 1
        connect()
    except pygatt.exceptions.BLEError:
        print("Error al conectar con el dispositivo")
        # Volvemos a intentar
        continue
    # Una vez conectado, enviamos la configuracion de la comunicacion
    status, protocol = db.getConfig()
    payload = bytearray([status, protocol])
    device.char_write(CHARACTERISTIC_UUID_CONFIG, payload) # Configuracion de la comunicacion
    # Guardamos en la BD la cantidad de intentos y el tiempo de conexion
    db.insertLoss(attempts, device.mac_address)