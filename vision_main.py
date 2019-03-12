#!/usr/bin/env python3
import time
import sys
import socket

from vision_camera import VisionCamera
from vision_config import VisionConfig
from vision_processor import VisionProcessor
from vision_output_server import VisionOutputServer
from vision_datahub import VisionDatahub
from pprint import pprint
from vision_log import Log

MAIN_VISION_CAMERA_INDEX = 0
ROBOT_IP = "10.60.27.2"
ROBOT_SERVER_PORT = 6060

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
        print("Failed to load configuration file '%s'" % visionConfig.frcConfigFile)
        sys.exit(1)

    log = Log.getInstance(visionConfig.config)

    # Wait for robot to start up before we try to use network tables
    robotWait(log)
    log.info('Robot is up, vision starting...', True)


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
        log.info("Vision Output Server started on port '%s'" % outputServerPort)
    else: 
        log.warn("Vision Output Server not started, no port given")

    # TODO: do we want to retry here?
    if not mainVisionCamera:
        log.error("No cameras found, exiting!")
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
                'distanceToTargetInches': vp.distanceToTargetInches
            }
            datahub.put(visionData)
            log.debug("Put to datahub: {" + ', '.join(['{}:{}'.format(k,v) for k,v in sorted(visionData.items())]) + "}")

        else:
            log.info("No frame to process")

        # TODO: Should we keep or not?    
        # time.sleep(0.0010)


def robotWait(log, maxAttempts=-1):
    robotIsReady = False
    numAttempts = 0
    while not robotIsReady:
        if maxAttempts > -1 and numAttempts >= maxAttempts:
            log.info("Maximum number of attempts ("+maxAttempts+") to check robot status reached", True)
            return False

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((ROBOT_IP, ROBOT_SERVER_PORT))
                s.sendall(b'vision-ping\n')
                data = s.recv(1024)
                log.info("data received back: " + repr(data))
                if data and data.decode('utf-8') == 'robot-pong\n':
                    robotIsReady = True
            except:
                robotIsReady = False

            if not robotIsReady:
                log.info('Robot not ready yet, will check again in 3 seconds...', True)
                time.sleep(3)

        numAttempts += 1

    return True