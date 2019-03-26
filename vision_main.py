#!/usr/bin/env python3
import time
import sys
import socket
import atexit
import ast
import os

from vision_camera import VisionCamera
from vision_config import VisionConfig
from vision_processor import VisionProcessor
from vision_output_server import VisionOutputServer
from vision_datahub import VisionDatahub
from vision_robot_client import VisionRobotClient
from pprint import pprint
from vision_log import Log
from vision_status import VisionStatus

# GLOBALS
MAIN_VISION_CAMERA_INDEX = 0
onExitInvoked = False
log = None
piTime = None
visionStatus = VisionStatus()

def onExit():
    global onExitInvoked
    global log
    global visionStatus

    if onExitInvoked:
        return

    visionStatus.clearAllStatus()

    onExitInvoked = True
    if log:
        log.info("Exiting vision_main", True)
    else:
        print("Exiting vision_main")


# MAIN
if __name__ == "__main__":
    try:
        atexit.register(onExit)
        visionStatus.setVisionUp(True)

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
            print("Failed to load configuration file '%s'" % visionConfig.frcConfigFile)
            sys.exit(1)


        log = Log.getInstance(visionConfig.config)

        robotClient = VisionRobotClient(log, visionStatus)
        robotClient.waitRobot()
        log.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        log.info('>>> Robot is up, vision starting...')
        log.info('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>', True)


        # For ouputting info to Network tables
        # Commenting out in order to use sockets instead
        # datahub = VisionDatahub(visionConfig.server, visionConfig.team)
        # datahub.start()

        mainVisionCamera = VisionCamera.getMainVisionCamera(visionConfig)
        visionOut = None
        # If outputServerPort is not set, then output server will not be started
        if outputServerPort:
            visionOut = VisionOutputServer()
            visionOut.setConfigValue('serverPort', None if outputServerPort == 'next' else int(outputServerPort))
            visionOut.start()
            log.info("Vision Output Server started on port '%s'" % outputServerPort)
        else: 
            log.warn("Vision Output Server not started, no port given")

        # TODO: do we want to retry here?
        if not mainVisionCamera:
            log.error("No cameras found, exiting!")
            sys.exit()

        vp = VisionProcessor(frameReadTimeout=0.3)
        # Ping robot every 5 seconds to ensure it's alive
        currentTimeMs = log.currentTimeMillis()
        nextRobotCheckTime = currentTimeMs + 5000

        visionDataStr = ''
        # loop forever
        while True:
            currentTimeMs = log.currentTimeMillis()
            if currentTimeMs >= nextRobotCheckTime:
                if not robotClient.waitRobot(2): # Wait a maximum of 2 attempts for 3 secs on each attempt
                    log.error("Lost communication with robot, exiting!")
                    break
                else:
                    # ping robot again 5 secs from now
                    nextRobotCheckTime = log.currentTimeMillis() + 5000

            # TODO: read the frame from the VisionCamera object instead?
            frame = vp.readCameraFrame(mainVisionCamera)
            if frame is not None:
                processedFrame = vp.processFrame(frame)                    
                vpLogMessages = vp.logMessages
                if visionOut: visionOut.postFrame(processedFrame)

                visionData = {
                    'contoursCenterX' : vp.contoursCenterPoint['x'],
                    'contoursCenterY' : vp.contoursCenterPoint['y'],
                    'numContours'     : vp.contourCount,
                    'contourAreaLeft' : vp.contourAreas[0] if len(vp.contourAreas) > 1 else -1,
                    'contourAreaRight': vp.contourAreas[1] if len(vp.contourAreas) > 1 else -1,
                    'distanceToTargetInches': vp.distanceToTargetInches
                }

#                timeStart = log.currentTimeMillis()
#                datahub.put(visionData)
                visionDataStr = ';'.join(['{}={}'.format(k,v) for k,v in sorted(visionData.items())])
                robotClient.sendToRobot("vision-data;"+visionDataStr)
#                timeEnd = log.currentTimeMillis()
#                log.info("send time: " + str(timeEnd-timeStart))
                vpLogMessages.append((Log.TRACE, "Put to robot: {" + visionDataStr + "}"))
                log.logFrameInfo(vpLogMessages)
                log.logFrame(processedFrame, VisionProcessor.writeFrame)

            else:
                log.info("No frame to process")
    except:  # catch any error
        if log:
            log.error("Unexpected error: "+ str(sys.exc_info()[0]))
        else:
            print("Unexpected error: "+ str(sys.exc_info()[0]))

        raise   # rethrow the error
    finally:
        onExit()