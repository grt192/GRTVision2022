from pipeline_thread import PipelineThread
from pipelines.example_pipeline import ExamplePipeline


def run_pipelines(lines, is_local=False):
    for pipeline in lines:
        # Create thread
        thread = PipelineThread(is_local, pipeline)
        thread.daemon = True
        thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print('Ending program...')


# Local pipeline test without CameraServer or NetworkTables
if __name__ == '__main__':
    pipelines = [ExamplePipeline('0', 0), ExamplePipeline('1', 1)]
    run_pipelines(pipelines, True)
