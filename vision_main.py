#!/usr/bin/env python3
import time
import sys

from vision_camera import VisionCamera
from vision_config import VisionConfig
from vision_processor import VisionProcessor
from vision_output_server import VisionOutputServer
from vision_datahub import VisionDatahub
from pprint import pprint

MAIN_VISION_CAMERA_INDEX = 0

if __name__ == "__main__":
    
    configFile = None
    outputServerPort = None

    #TODO: do better job of parsing command line
    if len(sys.argv) >= 3:
        if '-cfg' in sys.argv:
            configFile = sys.argv[sys.argv.index('-cfg') + 1]
        if '-oport' in sys.argv:
            outputServerPort = sys.argv[sys.argv.index('-oport') + 1]
            
    visionConfig = VisionConfig(configFile)

    # read configuration
    if not visionConfig.readConfig():
        print("Failed to load configuration file '%s'" % visionConfig.configFile)
        sys.exit(1)

    # For ouputting info to Network tables
    datahub = VisionDatahub(visionConfig.server, visionConfig.team)
    datahub.start()

    mainVisionCamera = VisionCamera.getMainVisionCamera(visionConfig)
    visionOut = None
    # If outputServerPort is not set, then output server will not be started
    if outputServerPort:
        visionOut = VisionOutputServer()
        visionOut.setConfigValue('serverPort', None if outputServerPort == 'next' else int(outputServerPort))
        visionOut.start()
        print("Vision Output Server started on port '%s'" % outputServerPort)
    else: 
        print("Vision Output Server not started, no port given")

    # TODO: do we want to retry here?
    if not mainVisionCamera:
        print("No cameras found, exiting!")
        sys.exit()

    vp = VisionProcessor(frameReadTimeout=0.3)
    # loop forever
    while True:
        # TODO: read the frame from the VisionCamera object instead?
        frame = vp.readCameraFrame(mainVisionCamera)
        if frame is not None:
            gripFrame = vp.processFrame(frame)
            if visionOut: visionOut.postFrame(gripFrame)

            visionData = {
                'contoursCenterX' : vp.contoursCenterPoint['x'],
                'contoursCenterY' : vp.contoursCenterPoint['y'],
                'numContours'     : vp.contourCount,
                'contourAreaLeft' : vp.contourAreas[0] if len(vp.contourAreas) > 1 else -1,
                'contourAreaRight': vp.contourAreas[1] if len(vp.contourAreas) > 1 else -1,
            }
            print("Put to datahub: {" + ', '.join('{}:{}'.format(*el) for el in visionData.items().sort()) + "}")

        else:
            print("No frame to process")

        # TODO: Should we keep or not?    
        # time.sleep(0.0010)
