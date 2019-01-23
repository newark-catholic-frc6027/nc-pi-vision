import cv2

class VisionProcessor:

    def __init__(self, frameReadTimeout=0.25):
        self.frameReadTimeout = frameReadTimeout

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

        cv2.drawMarker(frame, (160, 120), (0, 0, 255))
        return frame
