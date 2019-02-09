import cv2
from grip import GripPipeline
import datetime

class VisionProcessor:

    
    def __init__(self, frameReadTimeout=0.25):
        self.frameReadTimeout = frameReadTimeout
        self.gripPipeline = GripPipeline()
        self.contoursCenterPoint = {'x': None, 'y' : None}
        self.contourAreas = []
        self.contourCount = 0


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

        if self.gripPipeline.find_contours_output:
            print("##################################################")
            print("# of contours: %d" % len(self.gripPipeline.find_contours_output))
            i = 0
            numContours = len(self.gripPipeline.find_contours_output)
            self.contourCount = numContours
            print("num of contours: %d" % self.contourCount)

            if numContours >= 2 and numContours <= 3:

                contour_x_positions = []
                contour_y_positions = []
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
#                        contour_x_positions.append((i, cx))
#                        contour_y_positions.append((i, cy))                                       
                    area = cv2.contourArea(contour)
                    print("----  contour %s: area -> %s ----" % (str(i+1), str(area)))

                    contourInfo.append({'x': cx, 'y': cy, 'area': area})
#                    self.contourAreas.append((i, area))
                    i += 1
                    #perimeter = cv2.arcLength(contour, True)
                    #approx = cv2.approxPolyDP(contour, 0.05 * perimeter, True)
                #end for loop
                # sort list of contourInfo by x-coordinate
                contourInfo.sort(key=lambda c: c['x'])


#                print("area of contours: " % self.contourAreas)
                # Calculate the center between two contours (i.e. half the distance between the two contours)
#                center_x = -1
#                center_y = -1

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

#                if (len(contour_x_positions) == 2 and len(contour_y_positions) == 2):
                center_x = (contourInfo[0]['x'] + contourInfo[1]['x']) / 2.0
                center_y = (contourInfo[0]['y'] + contourInfo[1]['y']) / 2.0

                print('center = (' + str(center_x) + ', ' + str(center_y) + ')')
                self.contoursCenterPoint['x'] = center_x
                self.contoursCenterPoint['y'] = center_y
            else:
                #filter down to 2 contours
                print("!!!!!!!!!!!!!!!!!!! NOT 2 CONTOURS !!!!!!!!!!!!!!!!!!!")

        return self.gripPipeline.hsv_threshold_output
       
