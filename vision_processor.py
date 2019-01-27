import cv2
from grip import GripPipeline
import datetime

class VisionProcessor:

    
    def __init__(self, frameReadTimeout=0.25):
        self.frameReadTimeout = frameReadTimeout
        self.gripPipeline = GripPipeline()
        self.blobResult = 0

    def readCameraFrame(self, visionCamera):
        """
        Reads the latest frame from the camera server instance to pass to opencv
        :param camera: The camera to read from
        :return: The latest frame
        """

        cvSink = visionCamera.cameraServer.getVideo(camera=visionCamera.camera)
        frameTime, frame = cvSink.grabFrame(None, self.frameReadTimeout)

        if frameTime == 0:
            print("Failed to get a frame")
            return None

        return frame

    def processFrame(self, frame):
        # TODO, run grip pipeline
        self.gripPipeline.process(frame)
        if self.gripPipeline.find_blobs_output:
            print("##################################################")
            print("# of blobs: %d" % len(self.gripPipeline.find_blobs_output))

            i = 0
            keypoints = self.gripPipeline.find_blobs_output
            for keypoint in keypoints:
                print("> " + str(datetime.datetime.now()) + " points of keypoint " + str(i) + ":")
                print("coords:")
                print(*keypoint.pt)
                print("size: " + str(keypoint.size))
                i += 1

            if keypoints and len(keypoints) == 2:
                # Blobs are stored right to left in the array
                #                 right blob size   - left blob size
                self.blobResult = keypoints[0].size - keypoints[1].size
            else:
                self.blobResult = None

        return self.gripPipeline.rgb_threshold_output
        # cv2.drawMarker(frame, (160, 120), (0, 0, 255))
        # return frame
