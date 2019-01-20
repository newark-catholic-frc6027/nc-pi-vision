from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer
import json

class VisionCamera:

    def __init__(self, cameraConfig):
        self.cameraConfig = cameraConfig
        self.camera = None

    """Start running the camera."""
    def start(self):
        print("Starting camera '{}' on {}".format(self.cameraConfig.name, self.cameraConfig.path))
        inst = CameraServer.getInstance()
        self.camera = UsbCamera(self.cameraConfig.name, self.cameraConfig.path)
        server = inst.startAutomaticCapture(camera=self.camera, return_server=True)

        '''
        cv_sink = inst.getVideo(camera=camera)
        fooArray = None
        frametime, fooArray = cv_sink.grabFrame(fooArray, 0.5)
        print("frametime = %s" % frametime)
        print("error = %s" % cv_sink.getError())
        if frametime != 0:
            cv2.imwrite("foo.jpg", fooArray)

        '''
        self.camera.setConfigJson(json.dumps(self.cameraConfig.config))
        self.camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

        if self.cameraConfig.streamConfig is not None:
            server.setConfigJson(json.dumps(self.cameraConfig.streamConfig))

        return self.camera
