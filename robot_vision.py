#!/usr/bin/env python3
#----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import time
import sys
import json

from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer
from networktables import NetworkTablesInstance

from vision_config import VisionConfig

"""Start running the camera."""
def startCamera(config):
    print("Starting camera '{}' on {}".format(config.name, config.path))
    inst = CameraServer.getInstance()
    camera = UsbCamera(config.name, config.path)
    server = inst.startAutomaticCapture(camera=camera, return_server=True)

    '''
    cv_sink = inst.getVideo(camera=camera)
    fooArray = None
    frametime, fooArray = cv_sink.grabFrame(fooArray, 0.5)
    print("frametime = %s" % frametime)
    print("error = %s" % cv_sink.getError())
    if frametime != 0:
        cv2.imwrite("foo.jpg", fooArray)

    '''
    camera.setConfigJson(json.dumps(config.config))
    camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

    if config.streamConfig is not None:
        server.setConfigJson(json.dumps(config.streamConfig))

    return camera

if __name__ == "__main__":
    
    configFile = None
    if len(sys.argv) >= 2:
        configFile = sys.argv[1]


    visionConfig = VisionConfig(configFile)

    # read configuration
    if not visionConfig.readConfig():
        sys.exit(1)

    # start NetworkTables
    ntinst = NetworkTablesInstance.getDefault()
    if visionConfig.server:
        print("Setting up NetworkTables server")
        ntinst.startServer()
    else:
        print("Setting up NetworkTables client for team {}".format(visionConfig.team))
        ntinst.startClientTeam(visionConfig.team)

    # start cameras
    cameras = []
    for cameraConfig in visionConfig.cameraConfigs:
        cameras.append(startCamera(cameraConfig))

    # loop forever
    while True:
        time.sleep(10)
