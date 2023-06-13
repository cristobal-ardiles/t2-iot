import sqlite3 as sql
from datetime import datetime

# Documentación https://docs.python.org/3/library/sqlite3.html

def dataSave(header, data):
    with sql.connect("DB.sqlite") as con:
        cur = con.cursor()
        if header["ID_protocol"] == 0:
          cur.execute('''insert into Datos (ID_DEVICE, MAC, Status, BatteryLevel, Timestamp)
            values (?, ?, ?, ?, ?)''',
                       (header["ID_DEVICE"], header["MAC"], data['Status'], data['BatteryLevel'], data['Timestamp']))
          
        elif header["ID_protocol"] == 1:
            cur.execute('''insert into Datos (ID_DEVICE, MAC, Status, BatteryLevel, Timestamp, Temp, Pressure, Humidity, CO)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (header["ID_DEVICE"], header["MAC"], data['Status'], data['BatteryLevel'], data['Timestamp'], data['Temperature'], data['Pressure'], data['Humidity'], data['CO']))
        
        elif header["ID_protocol"] == 2:
            cur.execute('''insert into Datos (ID_DEVICE, MAC, Status, BatteryLevel, Timestamp, Temp, Pressure, Humidity, CO, RMS)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (header["ID_DEVICE"], header["MAC"], data['Status'], data['BatteryLevel'], data['Timestamp'], data['Temperature'], data['Pressure'], data['Humidity'], data['CO'], data['RMS']))
        
        elif header["ID_protocol"] == 3:
            cur.execute('''insert into Datos (ID_DEVICE, MAC, Status, BatteryLevel, Timestamp, Temp, Pressure, Humidity, CO, RMS, Amp_X, Frec_X, Amp_Y, Frec_Y, Amp_Z, Frec_Z)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (header["ID_DEVICE"], header["MAC"], data['Status'], data['BatteryLevel'], data['Timestamp'], data['Temperature'], data['Pressure'], data['Humidity'], data['CO'], data['RMS'], data['Amp_X'], data['Frec_X'], data['Amp_Y'], data['Frec_Y'], data['Amp_Z'], data['Frec_Z']))

def logSave(header):
    with sql.connect("DB.sqlite") as con:
        # Tiempo de llegada del paquete en el lado del servidor
        timestamp = datetime.now()
        cur = con.cursor()
        cur.execute('''insert into Logs (ID_DEVICE, MAC, TransportLayer, ID_protocol, Timestamp)
          values (?, ?, ?, ?)''',
                     (header["ID_DEVICE"], header["MAC"], header["TransportLayer"], header["ID_protocol"], timestamp))
        
def configSave(header):
    with sql.connect("DB.sqlite") as con:
        cur = con.cursor()
        cur.execute('''insert into Config (ID_protocol, TransportLayer)
          values (?, ?)''',
                     (header["ID_protocol"], header["TransportLayer"]))
        
def lossSave(header, data, attempts):
    with sql.connect("DB.sqlite") as con:
        cur = con.cursor()
        # We calculate the time from the first attempt to the last one
        data_timestamp = data["Timestamp"]
        current_timestamp = datetime.now() # When the connection is established
        comunication_delay_seconds = (current_timestamp - data_timestamp).total_seconds()

        cur.execute('''insert into Loss (ID_DEVICE, MAC, ConnectionTime, Attempts)
          values (?, ?, ?, ?)''',
                     (header["ID_DEVICE"], header["MAC"], comunication_delay_seconds, attempts))

def getConfig():
    with sql.connect("DB.sqlite") as con:
        cur = con.cursor()
        protocol, transport = cur.execute('''select ID_protocol, TransportLayer from Config''').fetchone()
        return protocol, transport
    
def save_config(status, protocol):
    with sql.connect("DB.sqlite") as con:
        cur = con.cursor()
        cur.execute(f'''UPDATE Config SET ID_protocol = {protocol}, TransportLayer = {status} 
                    WHERE ID_DEVICE = 12612''')
        con.commit()
    