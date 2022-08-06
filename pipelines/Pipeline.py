from abc import ABC, abstractclassmethod


class Pipeline(ABC):
    """
    A pipeline that produces data from processing input images.
    """

    @abstractclassmethod
    def process(self, frame):
        """
        Process a frame from the source.
        """
        pass