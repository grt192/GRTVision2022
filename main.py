from networktables import NetworkTables
from grip import LemonVisionGripPipeline

import cv2
import time

def main():
    input_port = 0
    num_ports = 4

    # Create a video capture
    cap = cv2.VideoCapture(input_port)
    _, frame = cap.read()

    # Keep trying until image is obtained
    while frame is None:

        print("Error: No image to process. Cannot run vision pipeline. Are images being captured from the camera?")

        # Try a different port
        input_port = (input_port + 1) % num_ports
        cap = cv2.VideoCapture(input_port)
        _, frame = cap.read()

        print("Trying /dev/video" + str(input_port))

        time.sleep(1)

    # Run the pipeline on the video stream
    while True:

        _, frame = cap.read()

        # Initalize the vision pipeline
        visionPipeline = LemonVisionGripPipeline()

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

        # Put test value in NT
        sd.putString('test', 'hello here is a test str value')

if __name__ == "__main__":
    print("MAIN")
    main()
