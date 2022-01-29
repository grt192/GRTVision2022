import cv2
from pipelines.pipeline_interface import PipelineInterface


class ExamplePipeline(PipelineInterface):
    def __init__(self, name='0', device_num=0, is_local=True):
        super().__init__(name, device_num, is_local)

    def process(self):
        # Initialize capture if necessary
        if self.cap is None:
            self.cap = self.get_capture()

        error_msg = None
        ret, frame = self.cap.read()
        self.frame = frame

        # If frame was received, process the frame 
        if ret:
            data = self.process_frame()

        # If no frame was received, re-capture
        else:
            self.cap = self.get_capture()
            error_msg = 'cannot get capture ' + str(self.device_num)

        return {'test': 'test!'}, error_msg

    def process_frame(self):
        cv2.circle(self.frame, (100, 100), 100, (0, 0, 255), 5)
        return {'test': 'test!'}

    def device_num(self):
        return self.device_num

    def get_name(self):
        return self.name
