import multiprocessing as mp
import threading
import logging
from networktables import NetworkTables
from pipeline_runner import run_pipelines
from pipelines.example_pipeline import ExamplePipeline

logging.basicConfig(level=logging.DEBUG)


# Connect to NetworkTables
def connect():
    # Start thread to connect to NetworkTables
    cond = threading.Condition()
    notified = [False]

    def connection_listener(connected, info):
        print(info, '; Connected=%s' % connected)
        with cond:
            notified[0] = True
            cond.notify()
  
    # Use RoboRIO static IP address
    # Don't use 'roborio-192-frc.local'. https://robotpy.readthedocs.io/en/stable/guide/nt.html#networktables-guide
    NetworkTables.initialize(server='10.1.92.2')
    NetworkTables.addConnectionListener(connection_listener, immediateNotify=True)

    with cond:
        print('Waiting')
        if not notified[0]:
            cond.wait()

    print('Connected to NetworkTables!')

    return NetworkTables.getTable('jetson')


roborio = connect()

# Set up multiprocessing
mp.set_start_method('fork')

# Run the pipelines
# pipelines = [ExamplePipeline('0', 0), ExamplePipeline('1', 1)]
pipelines = [ExamplePipeline('0', '/dev/cam/turret'), ExamplePipeline('1', '/dev/cam/intake')]
run_pipelines(pipelines, False, roborio)