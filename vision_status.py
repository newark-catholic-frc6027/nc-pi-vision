import RPi.GPIO as GPIO 

class VisionStatus:
    VISION_RUNNING_PIN = 8
    ROBOT_ALIVE_PIN = 8 # TODO: change

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(VisionStatus.VISION_RUNNING_PIN, GPIO.OUT, initial=GPIO.LOW)
        self.visionUp = False
        self.robotAlive = False
        self.error = False

    def setVisionUp(self, up=False):
        try:
            if up and not self.visionUp:
                GPIO.output(VisionStatus.VISION_RUNNING_PIN, GPIO.HIGH) # Turn on
            elif not up and self.visionUp:
                GPIO.output(VisionStatus.VISION_RUNNING_PIN, GPIO.LOW) # Turn off
        
            self.visionUp = up
        except:
            self.error = True

    def setRobotAlive(self, alive=False):
        try:
            #TODO: change to different PIN
            if alive and not self.robotAlive:
                GPIO.output(VisionStatus.VISION_RUNNING_PIN, GPIO.HIGH) # Turn on
            elif not alive and self.robotAlive:
                GPIO.output(VisionStatus.VISION_RUNNING_PIN, GPIO.LOW) # Turn off

            self.robotAlive = alive
        except:
            self.error = True

    def setAllStatus(self, status=False):
        self.setVisionUp(status)
        self.setRobotAlive(status)

    def clearAllStatus(self):
        self.setVisionUp(False)
        self.setRobotAlive(False)