import threading
from pipeline_thread import PipelineThread
from pipelines.example_pipeline import ExamplePipeline
from pipelines.example_pipeline2 import ExamplePipeline2


def run_pipelines(is_local, pipelines):

    for pipeline in pipelines:
        # Create thread
        thread = PipelineThread(is_local, pipeline)
        thread.daemon = True
        thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print('Ending program...')

if __name__ == '__main__':
    pipelines = [ExamplePipeline('0'), ExamplePipeline2('1')]
    run_pipelines(True, pipelines)

