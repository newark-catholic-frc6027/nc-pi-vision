import json
import sys
import configparser
import os.path

#   JSON format:
#   {
#       "team": <team number>,
#       "ntmode": <"client" or "server", "client" if unspecified>
#       "cameras": [
#           {
#               "name": <camera name>
#               "path": <path, e.g. "/dev/video0">
#               "pixel format": <"MJPEG", "YUYV", etc>   // optional
#               "width": <video mode width>              // optional
#               "height": <video mode height>            // optional
#               "fps": <video mode fps>                  // optional
#               "brightness": <percentage brightness>    // optional
#               "white balance": <"auto", "hold", value> // optional
#               "exposure": <"auto", "hold", value>      // optional
#               "properties": [                          // optional
#                   {
#                       "name": <property name>
#                       "value": <property value>
#                   }
#               ],
#               "stream": {                              // optional
#                   "properties": [
#                       {
#                           "name": <stream property name>
#                           "value": <stream property value>
#                       }
#                   ]
#               }
#           }
#       ]
#   }


class CameraConfig: pass

class VisionConfig:

    DEFAULT_FRC_CONFIG_FILE = "/boot/frc.json"
    DEFAULT_VISION_CONFIG_FILE = "./vision_cfg.ini"

    def __init__(self, frcConfigFile=None, visionConfigFile=None):
        self.team = None
        self.server = False
        self.cameraConfigs = []
        self.frcConfigFile = frcConfigFile or VisionConfig.DEFAULT_FRC_CONFIG_FILE
        self.visionConfigFile = visionConfigFile or VisionConfig.DEFAULT_VISION_CONFIG_FILE
        self.config = None


    """Report parse error."""
    def __parseError(self, str):
        print("config error in '" + self.frcConfigFile + "': " + str, file=sys.stderr)

    """Read single camera configuration."""
    def __readCameraConfig(self, config):
        cam = CameraConfig()

        # name
        try:
            cam.name = config["name"]
        except KeyError:
            self.__parseError("could not read camera name")
            return False

        # path
        try:
            cam.path = config["path"]
        except KeyError:
            self.__parseError("camera '{}': could not read path".format(cam.name))
            return False

        # stream properties
        cam.streamConfig = config.get("stream")

        cam.config = config

        self.cameraConfigs.append(cam)
        return True

    def readVisionConfig(self):
        self.config = configparser.ConfigParser()
        if self.visionConfigFile and os.path.isfile(self.visionConfigFile):
            try:
                self.config.read(self.visionConfigFile)
            except:
                print("Vision config file not found at '{}': {}".format(self.visionConfigFile, sys.exc_info()[0]))


    """Read configuration file."""
    def readConfig(self):
        self.readVisionConfig()
        # parse file
        try:
            with open(self.frcConfigFile, "rt") as f:
                j = json.load(f)
        except OSError as err:
            print("could not open '{}': {}".format(self.frcConfigFile, err), file=sys.stderr)
            return False

        # top level must be an object
        if not isinstance(j, dict):
            self.__parseError("must be JSON object")
            return False

        # team number
        try:
            self.team = j["team"]
        except KeyError:
            self.__parseError("could not read team number")
            return False

        # ntmode (optional)
        if "ntmode" in j:
            str = j["ntmode"]
            if str.lower() == "client":
                self.server = False
            elif str.lower() == "server":
                self.server = True
            else:
                self.__parseError("could not understand ntmode value '{}'".format(str))

        # cameras
        try:
            cameras = j["cameras"]
        except KeyError:
            self.__parseError("could not read cameras")
            return False
        for camera in cameras:
            if not self.__readCameraConfig(camera):
                return False


        return True
