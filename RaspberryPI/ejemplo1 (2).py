from time import sleep
import pygatt
from binascii import hexlify
# Conectar

MAC = "4C:EB:D6:61:FE:D6"
UUID_CHARACTERISTIC = "0000ee01-0000-1000-8000-00805f9b34fb"
adapter = pygatt.GATTToolBackend()

enable_notifications = bytearray([11,1,0,0,0,0]) # en hex es 0b0100000000 es de ejemplo, cambiar por el que se quiere seguir


def handle_notification(handle, value):
    """
    handle -- integer, characteristic read handle the data was received on
    value -- bytearray, the data returned in the notification
    """
    print("Received data: %s" % hexlify(value))

# Start connection
try:
    adapter.start()

    try:
        device = adapter.connect(MAC,timeout=20)
        print("Se conecto")
    except:
        print("Could not connect to the device, retrying...")
        device = adapter.connect(MAC,timeout=20)

    """
    #Send a connection key to the 0x29
    print("Pairing with the device...")
    device.char_write_handle(0x0029, connect_key)
    # Enable notifications by writing to 0x34
    device.char_write_handle(0x0034, enable_notifications)
    print("Connected with the device")
    input("Enter any key to quit...")
    """
    # Enable notifications by writing to 0x34
    # device.char_write_handle(0x0034, enable_notifications)

    #Subscribe and listen for notifications 
    try:
        device.subscribe(UUID_CHARACTERISTIC, callback=handle_notification, indication=True) # handle notifications es la funcion que corre cada vez que hay una notificacion
    except:
        try:
            device.subscribe(UUID_CHARACTERISTIC, callback=handle_notification) # se hace de neuvo por si hubo un error
        except:
            pass
finally:
    sleep(20)
    adapter.stop()