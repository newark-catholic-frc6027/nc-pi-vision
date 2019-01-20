#!/usr/bin/env python3
import time
import sys

from vision_camera import VisionCamera
from networktables import NetworkTablesInstance
from vision_config import VisionConfig

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


#    visionProcessor = Vision
    # start cameras
    visonCameras = []
    for cameraConfig in visionConfig.cameraConfigs:
        visionCamera = VisionCamera(cameraConfig)
        camera = visionCamera.start()
        if not camera:
            print("Failed to start camera '%s'" % cameraConfig.name)
            continue

        visonCameras.append(visionCamera)

    # loop forever
    while True:
        time.sleep(10)
