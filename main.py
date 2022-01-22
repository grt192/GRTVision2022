import threading
import logging
import subprocess
from pipeline import Pipeline
from consumers.example_consumer import ExampleConsumer

logging.basicConfig(level=logging.DEBUG)


# connect to NetworkTables
def connect():

    from networktables import NetworkTables

    # Start thread to connect to NetworkTables
    cond = threading.Condition()
    notified = [False]


    def connectionListener(connected, info):
        print(info, '; Connected=%s' % connected)
        with cond:
            notified[0] = True
            cond.notify()
  
    # Use RoboRIO static IP address
    # Don't use 'roborio-192-frc.local'. https://robotpy.readthedocs.io/en/stable/guide/nt.html#networktables-guide
    NetworkTables.initialize(server='10.1.92.2')
    NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

    with cond:
        print("Waiting")
        if not notified[0]:
            cond.wait()

    print("Connected to NetworkTables!")

    return NetworkTables.getTable('jetson')

roborio = connect()

try:
    consumers = [ExampleConsumer((300, 300), '0')]
    # Initialize pipeline with network table
    pipeline = Pipeline(consumers,
                        # ExampleConsumer((200, 400), '1')],
                        network_table=roborio)
    pipeline.start()
except KeyboardInterrupt: # Ctrl-C
    print('main.py KeyboardInterrupt')
