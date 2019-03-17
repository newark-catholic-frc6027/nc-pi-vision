import socket
#import atexit
import ast
import os
import time
import socket


class VisionRobotClient:
    ROBOT_IP = "localhost"
    ROBOT_SERVER_PORT = 5801

    def __init__(self, log):
#        self.log = log
        self.piTime = None

    def sendToRobot(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((VisionRobotClient.ROBOT_IP, VisionRobotClient.ROBOT_SERVER_PORT))
            reqData = "%s\n" % data
            s.sendall(reqData.encode())
            respData = s.recv(1024)
            print("data received back: " + repr(respData))
            if respData:
                # response is a python dict, convert it to a dict object
                response = ast.literal_eval(respData.decode('utf-8'))
                return response
            else:
                return {}


    def setPiTime(self, piTimeString):
        try:
#            os.system("sudo timedatectl set-time '%s'" % piTimeString)
            self.piTime = piTimeString
        except:
            self.piTime = '?'
            print('Failed to set Pi time')

    def waitRobot(self, maxAttempts=-1):
        robotIsReady = False
        numAttempts = 0
        while not robotIsReady:
            if maxAttempts > -1 and numAttempts >= maxAttempts:
                print("Maximum number of attempts ("+maxAttempts+") to check robot status reached")
                return False

            try:
                response = self.sendToRobot('vision-ping')
                if response['result'] == 'robot-pong':
                    robotIsReady = True
                    if not self.piTime:  # try to set the time on the pi
                        self.setPiTime(response['timestamp'])
            except:
                robotIsReady = False

                if not robotIsReady:
                    print('Robot not available, will check again in 3 seconds...')
                    time.sleep(3)

            numAttempts += 1

        return True
# MAIN
if __name__ == "__main__":
    client = VisionRobotClient(None)
    client.waitRobot()
    visionData = {
        'contoursCenterX' : None,
        'contoursCenterY' : 222,
        'numContours'     : 3,
        'contourAreaLeft' : 140.0,
        'contourAreaRight': -1,
        'distanceToTargetInches': 12.0
    }
    strToSend = "vision-data;"+';'.join(['{}={}'.format(k,v) for k,v in sorted(visionData.items())])
    client.sendToRobot(strToSend)