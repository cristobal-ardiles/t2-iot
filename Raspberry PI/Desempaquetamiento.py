from struct import unpack, pack
import traceback
import datetime as dt
from DatabaseWork import *

# Documentación struct unpack,pack :https://docs.python.org/3/library/struct.html#
'''
Estas funciones se encargan de parsear y guardar los datos recibidos.
Usamos struct para pasar de un array de bytes a una lista de numeros/strings. (https://docs.python.org/3/library/struct.html)
(La ESP32 manda los bytes en formato little-endian, por lo que los format strings deben empezar con <)

-dataSave: Guarda los datos en la BDD
-response: genera un OK para mandar de vuelta cuando se recibe un mensaje, con posibilidad de pedir que se cambie el status/protocol
-protUnpack: desempaca un byte array con los datos de un mensaje (sin el header)
-headerDict: Transforma el byte array de header (los primeros 10 bytes de cada mensaje) en un diccionario con la info del header
-dataDict: Transforma el byte array de datos (los bytes luego de los primeros 10) en un diccionario con los datos del mensaje

'''

    
def response(change:bool=False, status:int=255, protocol:int=255):
    OK = 1
    CHANGE = 1 if change else 0
    return pack("<BBBB", OK, CHANGE, status, protocol)

def parseData(packet):
    header = packet[:12] # Los primeros 12 bytes corresponden al header
    data = packet[12:] # El resto de los bytes corresponden a los datos
    header = getHeader(header) # Transformamos el header en un diccionario
    dataD = dataDict(header["ID_protocol"], data) # Transformamos los datos en un diccionario
    if dataD is not None:
        dataD["Timestamp"] = dt.datetime.fromtimestamp(dataD["Timestamp"])
        print("ID_device: " + str(header["ID_DEVICE"]) + " timestamp: " + str(dataD["Timestamp"]))
        dataSave(header, dataD) # Insertamos los datos a la base de datos

    return None if dataD is None else {**header, **dataD} #{header, dataD} #

def protUnpack(protocol:int, data):
    protocol_unpack = ["<BBl", "<BBlBfBf", "<BBlBfBff", "<BBlBfBfffffff"]
    return unpack(protocol_unpack[protocol], data)

def headerDict(data):
    id_device, M1, M2, M3, M4, M5, M6, transportlayer, protocol, leng_msg = unpack("<H6B2BH", data)
    MAC = ".".join([hex(x)[2:] for x in [M1, M2, M3, M4, M5, M6]])
    return {"ID_DEVICE":id_device, "MAC":MAC, "TransportLayer":transportlayer, "ID_protocol":protocol, "length":leng_msg}

def dataDict(protocol:int, data):
    if protocol not in [0, 1, 2, 3, 4, 5]:
        print("Error: protocol doesnt exist")
        return None
    def protFunc(protocol, keys):
        def p(data):
            unp = protUnpack(protocol, data)
            return {key:val for (key,val) in zip(keys, unp)}
        return p
    p0 = ["Status", "BatteryLevel", "Timestamp"]
    p1 = ["Status", "BatteryLevel", "Timestamp", "Temperature", "Pression", "Humidity", "CO"]
    p2 = ["Status", "BatteryLevel", "Timestamp", "Temperature", "Pression", "Humidity", "CO", "RMS"]
    p3 = ["Status", "BatteryLevel", "Timestamp", "Temperature", "Pression", "Humidity", "CO", "Amp_X", "Frec_X", "Amp_Y", "Frec_Y", "Amp_Z", "Frec_Z"]
    p4 = p1 = ["Status", "BatteryLevel", "Timestamp", "Temperature", "Pression", "Humidity", "CO", "Acc_x", "Acc_y", "Acc_z"]
    p = [p0, p1, p2, p3, p4]

    try:
        return protFunc(protocol, p[protocol])(data)
    except Exception:
        print("Data unpacking Error:", traceback.format_exc())
        return None
    

# ------------

def getHeader(data):
    """Receives a data packet and returns the header as a dictionary"""
    header = data[:12]
    return headerDict(header)