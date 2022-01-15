class ConsumerInterface:
    '''
    Process a frame, returning a tuple: 
    (Adjusted frame to send to camera stream, {dictionary: fields to send to network tables})
    '''
    def process_frame(self, frame):
        return (None, {})

    '''
    How often to process a frame.
    '''
    def process_interval(self):
        return 1000

    def stream_res(self):
        return (640, 360)

    '''
    Which device number does this pipeline use?
    '''
    def device_num(self):
        return 0

    def get_name(self):
        return "generic consumer name"