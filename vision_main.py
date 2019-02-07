#!/usr/bin/env python3
import time
import sys

from vision_camera import VisionCamera
from vision_config import VisionConfig
from vision_processor import VisionProcessor
from vision_output_server import VisionOutputServer
from vision_data_exchanger import VisionDataExchanger

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
    dataEx = VisionDataExchanger(visionConfig.server, visionConfig.team)
    dataEx.start()

    mainVisionCamera = VisionCamera.getMainVisionCamera(visionConfig)
    visionOutputServer = None
    # If outputServerPort is not set, then output server will not be started
    if outputServerPort:
        visionOutputServer = VisionOutputServer()
        visionOutputServer.setConfigValue('serverPort', None if outputServerPort == 'next' else int(outputServerPort))
        visionOutputServer.start()
        print("Vision Output Server started on port '%s'" % outputServerPort)
    else: 
        print("Vision Output Server not started, no port given")

    # TODO: do we want to retry here?
    if not mainVisionCamera:
        print("No cameras found, exiting!")
        sys.exit()

    visionProcessor = VisionProcessor(frameReadTimeout=0.3)
    # loop forever
    while True:
        # TODO: read the frame from the VisionCamera object instead?
        frame = visionProcessor.readCameraFrame(mainVisionCamera)
        if frame is not None:
            # TODO
            gripFrame = visionProcessor.processFrame(frame)
            if visionOutputServer:
                visionOutputServer.postFrame(gripFrame)

            ntContoursCenterX = visionProcessor.contoursCenterPoint['x']
            ntContoursCenterY = visionProcessor.contoursCenterPoint['y']
            ntNumContours = visionProcessor.contourCount
            contourAreas = visionProcessor.contourAreas
            if len(contourAreas)>1:

                ntContourAreaLeft = visionProcessor.contourAreas[1]
                ntContourAreaRight = visionProcessor.contourAreas[0]

            else:
                ntContourAreaLeft = ntContourAreaRight = -1

            print("Put to network table: {contoursCenterX: " + str(ntContoursCenterX) + 
                ", countoursCenterY: " +  str(ntContoursCenterY) + ", numOfContours: "+ str(ntNumContours) + 
                ", contourAreaLeft: "+ str(ntContourAreaLeft) + ", contourAreaRight: "+ str(ntContourAreaRight) + "}")

            dataEx.put('contoursCenterX', ntContoursCenterX)
            dataEx.put('contoursCenterY', ntContoursCenterY)
            dataEx.put('numContours', ntNumContours)
            dataEx.put('contourAreaLeft', ntContourAreaLeft)
            dataEx.put('contourAreaRight', ntContourAreaRight)

        else:
            print("No frame to process")

        # TODO: Should we keep or not?    
        # time.sleep(0.0010)
