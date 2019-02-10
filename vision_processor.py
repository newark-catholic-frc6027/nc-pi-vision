import cv2
import numpy as np
from grip import GripPipeline
import datetime
import math

class VisionProcessor:

    
    def __init__(self, frameReadTimeout=0.25):
        self.frameReadTimeout = frameReadTimeout
        self.gripPipeline = GripPipeline()
        self.contoursCenterPoint = {'x': None, 'y' : None}
        self.contourAreas = []
        self.contourCount = 0
        self.colors = [(0,0,255), (0,255,0), (255,0,0)]


    def readCameraFrame(self, visionCamera):
        """
        Reads the latest frame from the camera server instance to pass to opencv
        :param camera: The camera to read from
        :return: The latest frame
        """

        cvSink = visionCamera.cameraServer.getVideo(camera=visionCamera.camera)
        frameTime, frame = cvSink.grabFrame(None, self.frameReadTimeout)

        if frameTime == 0:
            print("Failed to get a frame")
            return None

        return frame

    def processFrame(self, frame):
        # TODO, run grip pipeline
        self.contoursCenterPoint['x'] = -1.0
        self.contoursCenterPoint['y'] = -1.0
        self.gripPipeline.process(frame)
        self.contourAreas = []
        self.contourCount = 0

        outputFrame = self.gripPipeline.hsv_threshold_output

        if self.gripPipeline.find_contours_output:
            print("##################################################")
            print("# of contours: %d" % len(self.gripPipeline.find_contours_output))
            i = 0
            numContours = len(self.gripPipeline.find_contours_output)
            self.contourCount = numContours
            print("num of contours: %d" % self.contourCount)

            if numContours >= 2 and numContours <= 3:
                contourInfo = []
                # Find the centers of mass of the contours
                # https://docs.opencv.org/3.4.2/dd/d49/tutorial_py_contour_features.html
                
                for contour in self.gripPipeline.find_contours_output:
                    moments = cv2.moments(contour)
                    cx = -1
                    cy = -1
                    if moments is not None and moments['m00'] is not None and moments['m00'] != 0.0:
                        cx = int(moments['m10'] / moments['m00'])
                        cy = int(moments['m01'] / moments['m00'])
                    #end if

                    area = cv2.contourArea(contour)
                    rect = cv2.minAreaRect(contour)
                    box = cv2.boxPoints(rect)
#                    x,y,w,h = cv2.boundingRect(contour)
#                    outputFrame = cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                    box = np.int0(box)
                    outputFrame = cv2.drawContours(frame,[box],0,self.colors[i],2)
                    print("----  contour %s: area = %s----" % (str(i+1), str(area)))

                    # Sort by y coords and grab points with smallest y (topPt) and next to largest y (botPt)
                    sortedPts = sorted(box, key=lambda pt: pt[1])
                    topPt = sortedPts[0]
                    botPt = sortedPts[2]
                    print("topPt(x,y) = %s,%s; botPt(x,y) = %s,%s" % (str(topPt[0]), str(topPt[1]), str(botPt[0]), str(botPt[1])))
                    slope = (topPt[1] - botPt[1])/(topPt[0] - botPt[0])
                    angle = math.degrees(math.atan(slope))


                    contourInfo.append({'x': cx, 'y': cy, 'area': area, 'angle': angle})
#                    self.contourAreas.append((i, area))
                    i += 1
                    #perimeter = cv2.arcLength(contour, True)
                    #approx = cv2.approxPolyDP(contour, 0.05 * perimeter, True)
                #end for loop

                # sort list of contourInfo by x-coordinate
                contourInfo.sort(key=lambda c: c['x'])
                j = 0
                for c in contourInfo:
                    j += 1
                    print("---- SORTED contour %s: area = %s; x = %s; angle = %s----" % (str(j), str(c['area']), str(c['x']), str(c['angle'])))
                

                # Trim the contours down to the two we are interested in which is the
                # two that are farthest apart
                removedContourArea = None
                removedIndex = -1
                if numContours == 3 and len(contourInfo) == 3:
                    x1 = contourInfo[0]['x']
                    x2 = contourInfo[1]['x']
                    x3 = contourInfo[2]['x']
                    x1_x2_diff = abs(x2-x1)
                    x2_x3_diff = abs(x3-x2)

                    if x1_x2_diff >= x2_x3_diff:
                        removedIndex = 3
                        removedContourArea = contourInfo[2]['area']
                        del contourInfo[2]
                    else:
                        removedIndex = 1
                        removedContourArea = contourInfo[0]['area']
                        del contourInfo[0]
                    #end if
                # end if

                self.contourAreas.append(contourInfo[0]['area'])
                self.contourAreas.append(contourInfo[1]['area'])
                print('area of contours: [%s], thrownOut[%s] -> %s' % (', '.join(map(str, self.contourAreas)), str(removedIndex), str(removedContourArea)))

                center_x = (contourInfo[0]['x'] + contourInfo[1]['x']) / 2.0
                center_y = (contourInfo[0]['y'] + contourInfo[1]['y']) / 2.0

                print('center = (' + str(center_x) + ', ' + str(center_y) + ')')
                self.contoursCenterPoint['x'] = center_x
                self.contoursCenterPoint['y'] = center_y
            else:
                #filter down to 2 contours
                print("!!!!!!!!!!!!!!!!!!! NOT 2 CONTOURS !!!!!!!!!!!!!!!!!!!")

        return outputFrame
       
