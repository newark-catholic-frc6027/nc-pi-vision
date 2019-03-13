import cv2
import numpy as np
from grip import GripPipeline
import datetime
import math
from vision_log import Log

class VisionProcessor:
    COLOR_RED =   (0, 0, 255)
    COLOR_GREEN = (0, 255, 0)
    COLOR_BLUE =  (255, 0, 0)
    FRAME_CENTER_X = 160
    FRAME_WIDTH = 320
    FRAME_HEIGHT = 240
    FRAME_CENTER = (160, 120)
    MAX_CONTOUR_THRESHOLD = 7
    CENTER_X_THRESHOLD = 20
    
    def __init__(self, frameReadTimeout=0.25):
        self.frameReadTimeout = frameReadTimeout
        self.gripPipeline = GripPipeline()
        self.contoursCenterPoint = {'x': None, 'y' : None}
        self.contourAreas = []
        self.contourCount = 0
        self.colors = [VisionProcessor.COLOR_RED, VisionProcessor.COLOR_GREEN, VisionProcessor.COLOR_BLUE]
        self.outputFrame = None
        self.foundContourPair = False
        self.contourPairCenterX = -1
        self.distanceToTargetInches = -1
        self.log = Log.getInstance()
        self.logMessages = []


    def readCameraFrame(self, visionCamera):
        """
        Reads the latest frame from the camera server instance to pass to opencv
        :param camera: The camera to read from
        :return: The latest frame
        """

        cvSink = visionCamera.cameraServer.getVideo(camera=visionCamera.camera)
        frameTime, frame = cvSink.grabFrame(None, self.frameReadTimeout)

        if frameTime == 0:
            self.log.error("Failed to get a frame")
            return None

        return frame

    def processFrame(self, frame):
        self.logMessages = []
        self.outputFrame = frame
        self.contoursCenterPoint['x'] = -1.0
        self.contoursCenterPoint['y'] = -1.0
        self.gripPipeline.process(frame)
        self.contourAreas = []
        self.contourCount = 0
        self.foundContourPair = False
        self.contourPairCenterX = -1
        self.distanceToTargetInches = -1


        outputFrame = self.gripPipeline.hsv_threshold_output

        if self.gripPipeline.find_contours_output:
            self.logMessages.append((Log.DEBUG, "##################################################"))
            self.logMessages.append((Log.DEBUG, "# of contours: %d" % len(self.gripPipeline.find_contours_output)))
#            i = 0
            numContours = len(self.gripPipeline.find_contours_output)
            self.contourCount = numContours
            self.logMessages.append((Log.DEBUG, "num of contours: %d" % self.contourCount))

            contourInfoList = self.generateContourInfo(frame, self.gripPipeline.find_contours_output)
            if len(contourInfoList) < VisionProcessor.MAX_CONTOUR_THRESHOLD:
                contourInfoList = self.findBestContours(frame, contourInfoList)
            else:
                #filter down to 2 contours
                self.logMessages.append((Log.INFO, "!!!!!!!!!!!!!!!!!!! TOO MANY CONTOURS !!!!!!!!!!!!!!!!!!!"))


            if len(contourInfoList) == 2:
                self.contourAreas.append(contourInfoList[0].area)
                self.contourAreas.append(contourInfoList[1].area)
                self.logMessages.append((Log.DEBUG, 'area of contours: [%s]' % (', '.join(map(str, self.contourAreas)))))

                center_x = (contourInfoList[0].centerX + contourInfoList[1].centerX) / 2.0
                center_y = (contourInfoList[0].centerY + contourInfoList[1].centerY) / 2.0

                self.logMessages.append((Log.DEBUG, 'center = (' + str(center_x) + ', ' + str(center_y) + ')'))
                self.contoursCenterPoint['x'] = center_x
                self.contoursCenterPoint['y'] = center_y

                self.calculateDistanceToTarget(contourInfoList[0], contourInfoList[1])

            else:
                #filter down to 2 contours
                self.logMessages.append((Log.INFO, "!!!!!!!!!!!!!!!!!!! NOT 2 CONTOURS !!!!!!!!!!!!!!!!!!!"))

        self.outputFrame = self.drawCenter(self.outputFrame)
        return self.outputFrame

    def drawCenter(self, frame):
        outputFrame = None
        if self.foundContourPair and self.contourPairCenterX and abs(self.contourPairCenterX-VisionProcessor.FRAME_CENTER_X) <= VisionProcessor.CENTER_X_THRESHOLD:
            color = VisionProcessor.COLOR_GREEN
        else: 
            color = VisionProcessor.COLOR_RED

        outputFrame = cv2.line(
            frame, 
            (VisionProcessor.FRAME_CENTER[0], VisionProcessor.FRAME_CENTER[1]-40), 
            (VisionProcessor.FRAME_CENTER[0], VisionProcessor.FRAME_CENTER[1]-10),
            color, 
            2
        )

        outputFrame = cv2.line(
            frame, 
            (VisionProcessor.FRAME_CENTER[0], VisionProcessor.FRAME_CENTER[1]+40), 
            (VisionProcessor.FRAME_CENTER[0], VisionProcessor.FRAME_CENTER[1]+10),
            color, 
            2
        )

        return outputFrame

    def generateContourInfo(self, currentFrame, gripContours):
        i = 0
        contourInfoList = []
        for contour in gripContours:
            moments = cv2.moments(contour)
            cx = -1
            cy = -1
            if moments is not None and moments['m00'] is not None and moments['m00'] != 0.0:
                cx = int(moments['m10'] / moments['m00'])
                cy = int(moments['m01'] / moments['m00'])
            #end if

            # Area of the contour
            area = cv2.contourArea(contour)
            # Calculate and draw a frame in red around the contour
            rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            self.logMessages.append((Log.DEBUG, "----  contour %s: area = %s----" % (str(i+1), str(area))))

            # Sort by y coords and grab points with smallest y (topPt) and next to largest y (botPt)
            sortedPts = sorted(box, key=lambda pt: pt[1])
            topPt = sortedPts[0]
            botPt = sortedPts[2]
            self.logMessages.append((Log.DEBUG, "topPt(x,y) = %s,%s; botPt(x,y) = %s,%s" % (str(topPt[0]), str(topPt[1]), str(botPt[0]), str(botPt[1]))))
            slope = (topPt[1] - botPt[1])/(topPt[0] - botPt[0])
            angle = math.degrees(math.atan(slope))


            contourInfoList.append(ContourInfo(contour, cx, cy, area, angle, [box]))
            i += 1
            #perimeter = cv2.arcLength(contour, True)
            #outputFrame = cv2.drawContours(frame, [box], 0, self.colors[i], 2)

        # sort the contours in ascending order by their center X coordinate
        contourInfoList.sort(key=lambda c: c.centerX)

        # Print list of sorted contours
        i = 0
        for c in contourInfoList:
            i += 1
            self.logMessages.append((Log.INFO, "---- SORTED contour %s: area = %s; x = %s; angle = %s----" % (str(i), str(c.area), str(c.centerX), str(c.angle))))
        
        return contourInfoList

    def findBestContours(self, currentFrame, contourInfoList):
        numContours = len(contourInfoList)
        if contourInfoList is None or numContours == 0:
            self.logMessages.append((Log.WARN, "!!!!!!!!!!!!!!!!!!! NO CONTOURS !!!!!!!!!!!!!!!!!!!"))
            return []

        returnContourInfoList = []
        if numContours == 1:
            contour = contourInfoList[0]
            self.drawOutline(currentFrame, contour.contourBox, VisionProcessor.COLOR_RED)
            returnContourInfoList = []
        elif numContours == 2:
            contourLeft = contourInfoList[0]
            contourRight = contourInfoList[1]
            # We are looking for contours in this configuration:  / \
            # where the first contour has a negative angle and the second
            # contour has a positive angle
            if contourLeft.angle >= 0:
                self.drawOutline(currentFrame, contourLeft.contourBox, VisionProcessor.COLOR_RED)
                self.drawOutline(currentFrame, contourRight.contourBox, VisionProcessor.COLOR_RED)
                returnContourInfoList = []
            else:  # this is a valid target and we can just retrn the list of contours we were given
                self.drawOutline(currentFrame, contourLeft.contourBox, VisionProcessor.COLOR_GREEN)
                self.drawOutline(currentFrame, contourRight.contourBox, VisionProcessor.COLOR_GREEN)
                returnContourInfoList = contourInfoList
                self.contourPairCenterX = (contourLeft.centerX + contourRight.centerX) / 2.0

        elif numContours == 3:
            # Possibilities are this:
            #  case 1 => /  \  /   or  case 2 =>  \  /  \ 
            contourLeft = contourInfoList[0]
            contourCenter = contourInfoList[1]
            contourRight = contourInfoList[2]
            # find two that belong to a pair, color in green and return the contours
            if contourLeft.angle < 0 and contourCenter.angle > 0 and contourRight.angle <= 0:
                # case 1, color first two in green, third in red
                self.drawOutline(currentFrame, contourLeft.contourBox, VisionProcessor.COLOR_GREEN)
                self.drawOutline(currentFrame, contourCenter.contourBox, VisionProcessor.COLOR_GREEN)
                self.drawOutline(currentFrame, contourRight.contourBox, VisionProcessor.COLOR_RED)
                returnContourInfoList = [contourLeft, contourCenter]
                self.contourPairCenterX = (contourLeft.centerX + contourCenter.centerX) / 2.0

            elif contourLeft.angle >= 0 and contourCenter.angle < 0 and contourRight.angle > 0:
                # case 2, color first in red, last two in green
                self.drawOutline(currentFrame, contourLeft.contourBox, VisionProcessor.COLOR_RED)
                self.drawOutline(currentFrame, contourCenter.contourBox, VisionProcessor.COLOR_GREEN)
                self.drawOutline(currentFrame, contourRight.contourBox, VisionProcessor.COLOR_GREEN)
                returnContourInfoList = [contourCenter, contourRight]
                self.contourPairCenterX = (contourCenter.centerX + contourRight.centerX) / 2.0
            else:
                self.drawOutline(currentFrame, contourLeft.contourBox, VisionProcessor.COLOR_RED)
                self.drawOutline(currentFrame, contourCenter.contourBox, VisionProcessor.COLOR_RED)
                self.drawOutline(currentFrame, contourRight.contourBox, VisionProcessor.COLOR_RED)
                returnContourInfoList = []
        elif numContours >= 4:
            # find all the contour pairs, which are contours in this configuration: /  \
            contourPairs = []
            # Ignore any initial contours with a 0/positive angle, we are looking for the
            # first contour with a negative angle
            startPairContourInfo = None
            startPairContourIndex = 0
            curIndex = 0
            for curContourInfo in contourInfoList:
                if curContourInfo.angle < 0:
                    # Since angle < 0, this should be the start of a pair
                    startPairContourInfo = curContourInfo
                    startPairContourIndex = curIndex
                else: # angle >= 0, could be the last contour in a pair
                    # If the index of the current contour is one greater
                    # than the index of the last starting contour found,
                    # this should be the second contour in the pair   
                    if curIndex == startPairContourIndex + 1:
                        if startPairContourInfo is not None:
                            # Add the pair of contours to our list of contour pairs
                            # and reset to look for another pair
                            # Append tuple with following values:
                            #  0 - First contour of the pair
                            #  1 - Second contour of the pair
                            #  2 - (center X value of second contour + center X value of start contour) / 2
                            self.logMessages.append((Log.DEBUG, "curIndex = %s, startPairContourIndex = %s, curContourInfo.angle = %s" 
                                % (str(curIndex), str(startPairContourIndex), str(curContourInfo.angle))))

                            contourPairs.append((
                                startPairContourInfo, 
                                curContourInfo, 
                                (curContourInfo.centerX + startPairContourInfo.centerX)/2.0
                            ))
                        # end if 
                        startPairContourIndex = 0
                        startPairContourInfo = None
                    else:
                        # we haven't found the second contour of the pair, reset to
                        # look for another pair
                        startPairContourIndex = 0
                        startPairContourInfo = None
                    # end if
                # end if

                curIndex += 1
            # end for

            if len(contourPairs) > 0:
                index = 0
                bestPairIndex = 0
                contourPairClosestToCenter = contourPairs[0]
                # center
                bestPairDeltaFromCenter = abs(contourPairClosestToCenter[2] - VisionProcessor.FRAME_CENTER_X)
                for contourTuple in contourPairs:
                    currentPairCenterX = contourTuple[2]
                    currentPairDeltaFromCenter =  abs(currentPairCenterX - VisionProcessor.FRAME_CENTER_X)
                    if currentPairDeltaFromCenter < bestPairDeltaFromCenter:
                        bestPairIndex = index
                        contourPairClosestToCenter = contourTuple
                        bestPairDeltaFromCenter = currentPairDeltaFromCenter
                    #end if
                    index += 1
                #end for
                
                # Now loop through all the pairs and color the best pair green
                self.drawOutline(currentFrame, contourPairClosestToCenter[0].contourBox, VisionProcessor.COLOR_GREEN)
                self.drawOutline(currentFrame, contourPairClosestToCenter[1].contourBox, VisionProcessor.COLOR_GREEN)
                self.contourPairCenterX = (contourPairClosestToCenter[1].centerX + contourPairClosestToCenter[0].centerX) / 2.0
                alreadyColoredContours = [contourPairClosestToCenter[0], contourPairClosestToCenter[1]]
                returnContourInfoList = alreadyColoredContours
                    # end if
                # end for
                # color remaining contours red
                for contourInfo in contourInfoList:
                    if not (contourInfo in alreadyColoredContours):
                        self.drawOutline(currentFrame, contourInfo.contourBox, VisionProcessor.COLOR_RED)
                    # end if
                # end for
            else:
                # color them all red
                returnContourInfoList = []
                for contour in contourInfoList:
                    self.drawOutline(currentFrame, contour.contourBox, VisionProcessor.COLOR_RED)
            #end if

        # end if
        self.foundContourPair = len(returnContourInfoList) == 2   
        return returnContourInfoList

    def drawOutline(self, currentFrame, contourBox, color):
        self.outputFrame = cv2.drawContours(currentFrame, contourBox, 0, color, 2)

    def calculateDistanceToTarget(self, leftContourInfo, rightContourInfo):
        contourAreaAvg = (leftContourInfo.area + rightContourInfo.area) / 2.0
        a1 = 191.58159
        a2 = 5.98129
        x0 = 78.95908
        p = 0.69955

        self.distanceToTargetInches = a2 + ((a1 - a2)/(1 + pow(contourAreaAvg/x0, p)))


class ContourInfo:
    def __init__(self, contour, centerX, centerY, area, angle, contourBox):
        self.contour = contour
        self.centerX = centerX
        self.centerY = centerY
        self.area = area
        self.angle = angle
        self.contourBox = contourBox
