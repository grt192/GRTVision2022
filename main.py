import threading
import logging
import subprocess
from pipeline_runner import run_pipelines
from pipelines.example_pipeline import ExamplePipeline
from pipelines.example_pipeline2 import ExamplePipeline2

logging.basicConfig(level=logging.DEBUG)


# Connect to NetworkTables
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

# Run the pipelines
pipelines = [ExamplePipeline('0'), ExamplePipeline2('1')]
run_pipelines(False, pipelines)
