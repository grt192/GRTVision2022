from abc import ABC, abstractclassmethod


class Source(ABC):
    """
    A source of images to be used by a processing pipeline. Can be a webcam or a loader for static images for testing.
    """

    @abstractclassmethod
    def get_frame(self):
        """
        Get a new frame.
        """
        pass