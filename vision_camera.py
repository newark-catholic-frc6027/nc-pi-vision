from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer
import json
from vision_config import VisionConfig


class VisionCamera:
    visionCameras = None

    @staticmethod
    def initCameras(visionConfig):
        '''
        :param visionConfig: a VisionConfig object with the frc pi camera configuration
        :return: A list of initialized cameras, in the form of VisionCamera objects, 
          that are connected to the pi
        '''
        if VisionCamera.visionCameras is None:
            VisionCamera.visionCameras = []
            for cameraConfig in visionConfig.cameraConfigs:
                visionCamera = VisionCamera(cameraConfig)
                camera = visionCamera.start()
                if not camera:
                    print("Failed to start camera '%s'" % cameraConfig.name)
                    continue

                VisionCamera.visionCameras.append(visionCamera)

        return VisionCamera.visionCameras

    @staticmethod
    def getMainVisionCamera(visionConfig):
        VisionCamera.initCameras(visionConfig)
        mainVisionCamera = None
        if len(VisionCamera.visionCameras) > 0:
            mainVisionCamera = VisionCamera.visionCameras[0]

        return mainVisionCamera


    def __init__(self, cameraConfig):
        self.cameraConfig = cameraConfig
        self.camera = None
        self.cameraServer = CameraServer.getInstance()

    """Start running the camera."""
    def start(self):
        print("Starting camera '{}' on {}".format(self.cameraConfig.name, self.cameraConfig.path))
        self.camera = UsbCamera(self.cameraConfig.name, self.cameraConfig.path)
        server = self.cameraServer.startAutomaticCapture(camera=self.camera, return_server=True)

        self.camera.setConfigJson(json.dumps(self.cameraConfig.config))
        self.camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

        if self.cameraConfig.streamConfig is not None:
            server.setConfigJson(json.dumps(self.cameraConfig.streamConfig))

        return self.camera