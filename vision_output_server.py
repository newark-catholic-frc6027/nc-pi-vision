from cscore import CameraServer

DEFAULT_SERVER_CONFIG = {
    'serverPort': None,  # will use next available port by default
    'name': 'grip',
    'displayName': 'displayName',
    'frameWidth': 320,
    'frameHeight': 240
}
class VisionOutputServer:

    def __init__(self, serverConfig=DEFAULT_SERVER_CONFIG):
        self.cfg = serverConfig
        self.cvSource = None

    def setConfigValue(self, name, value):
        self.cfg[name] = value

    def start(self):
        """
        Start up an output source and server to ouput custom frames
        """
        if not self.cvSource:
            cameraServer = CameraServer.getInstance()
            sink = cameraServer.addServer(name=self.cfg['name'], port=self.cfg['serverPort'])
            self.cvSource = cameraServer.putVideo(
                self.cfg['displayName'],
                self.cfg['frameWidth'],
                self.cfg['frameHeight']
            )
            sink.setSource(self.cvSource)

        return self.cvSource

    def postFrame(self, frame):
        if self.cvSource:
            self.cvSource.putFrame(frame)