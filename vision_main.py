#!/usr/bin/env python3
import time
import sys

from vision_camera import VisionCamera
from networktables import NetworkTablesInstance
from vision_config import VisionConfig
from vision_processor import VisionProcessor

MAIN_VISION_CAMERA_INDEX = 0

if __name__ == "__main__":
    
    configFile = None
    if len(sys.argv) >= 2:
        configFile = sys.argv[1]

    visionConfig = VisionConfig(configFile)

    # read configuration
    if not visionConfig.readConfig():
        print("Failed to load configuration file '%s'" % visionConfig.configFile)
        sys.exit(1)

    # start NetworkTables
    ntinst = NetworkTablesInstance.getDefault()
    if visionConfig.server:
        print("Setting up NetworkTables server")
        ntinst.startServer()
    else:
        print("Setting up NetworkTables client for team {}".format(visionConfig.team))
        ntinst.startClientTeam(visionConfig.team)

    mainVisionCamera = VisionCamera.getMainVisionCamera(visionConfig)

    # TODO: do we want to retry here?
    if not mainVisionCamera:
        print("No cameras found, exiting!")
        sys.exit()

    visionProcessor = VisionProcessor(frameReadTimeout=0.3)
    # loop forever
    while True:
        frame = visionProcessor.readCameraFrame(mainVisionCamera)
        if frame is not None:
            # TODO
            visionProcessor.processFrame(frame)
        else:
            print("No frame to process")

        # TODO: Should we keep or not?    
        time.sleep(10)
