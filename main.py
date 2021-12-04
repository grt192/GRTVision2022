from networktables import NetworkTables
from grip import LemonVisionGripPipeline

import cv2

def main():
    # Get the video capture from input 0
    capture = cv2.VideoCapture("/dev/video0")

    while True:
        # Capture a frame
        ret, frame = capture.read()

        # Initalize the vision pipeline
        visionPipeline = LemonVisionGripPipeline()

        if frame is None:
            print("Error: No image to process. Cannot run vision pipeline. Are images being captured from the camera?")
            continue

        # Process the frame
        visionPipeline.process(frame)

        # Retrieve the blobs from the pipeline
        print("Printing the blobs we received from the pipeline...")
        blobs = visionPipeline.find_blobs_output # Tuple of KeyPoint objects

        print(str(len(blobs)) + "-size tuple of type KeyPoint")

        xCentroids = []
        yCentroids = []

        # Append the centroid of blobs to the output array
        for i in range(len(blobs)):
            x, y = blobs[i].pt
            xCentroids.append(x)
            yCentroids.append(y)

        # Publish centroids on NetworkTables
        NetworkTables.initialize(server='roborio-192-frc.local')

        sd = NetworkTables.getTable('jetson')

        sd.putNumberArray('xCentroids', xCentroids)
        sd.putNumberArray('yCentroids', yCentroids)

@staticmethod
def publish_nt(blob_input):
    print("Beginning to publish to NetworkTables\n")

    print(blob_input[0])

    NetworkTables.initialize(server='roborio-192-frc.local')

    sd = NetworkTables.getTable('jetson')

    sd.putNumber('someNumber', 1234)
    # otherNumber = sd.getNumber('otherNumber')

if __name__ == "__main__":
    print("MAIN")
    main()
