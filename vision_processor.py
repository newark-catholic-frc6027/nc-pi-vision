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

            
            if numContours == 2:
                contour_x_positions = []
                contour_y_positions = []

                # Find the centers of mass of the contours
                # https://docs.opencv.org/3.4.2/dd/d49/tutorial_py_contour_features.html
                
                for contour in self.gripPipeline.find_contours_output:
                    print("----  contour %d ----" % i)
                    moments = cv2.moments(contour)
                    if moments is not None and moments['m00'] is not None and moments['m00'] != 0.0:
                        cx = int(moments['m10'] / moments['m00'])
                        cy = int(moments['m01'] / moments['m00'])
                        contour_x_positions.append(cx)
                        contour_y_positions.append(cy)
                    
                    
                    area = cv2.contourArea(contour)
                    self.contourAreas.append(area)
                    #perimeter = cv2.arcLength(contour, True)
                    #approx = cv2.approxPolyDP(contour, 0.05 * perimeter, True)
                #end for loop

                print("area of contours: " % self.contourAreas)

                # Calculate the center between two contours (i.e. half the distance between the two contours)
                center_x = -1
                center_y = -1

                if (len(contour_x_positions) == 2 and len(contour_y_positions) == 2):
                    center_x = (contour_x_positions[0] + contour_x_positions[1]) / 2.0
                    center_y = (contour_y_positions[0] + contour_y_positions[1]) / 2.0

                print('center = (' + str(center_x) + ', ' + str(center_y) + ')')
                self.contoursCenterPoint['x'] = center_x
                self.contoursCenterPoint['y'] = center_y

            else:
                #filter down to 2 contours
                print("!!!!!!!!!!!!!!!!!!! NOT 2 CONTOURS !!!!!!!!!!!!!!!!!!!")

        return self.gripPipeline.hsv_threshold_output
       
