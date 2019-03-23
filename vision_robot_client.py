import socket
#import atexit
import ast
import os
import time
import socket


class VisionRobotClient:
    ROBOT_IP = "10.60.27.2"
    ROBOT_SERVER_PORT = 5801

    def __init__(self, log):
        self.log = log
        self.piTime = None

    def sendToRobot(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((VisionRobotClient.ROBOT_IP, VisionRobotClient.ROBOT_SERVER_PORT))
#                self.log.trace("sending data: " + repr(data))
                reqData = "%s\n" % data
                s.sendall(reqData.encode())
                respData = s.recv(1024)
#                self.log.trace("data received back: " + repr(respData))
                if respData:
                    # response is a python dict, convert it to a dict object
                    response = ast.literal_eval(respData.decode('utf-8'))
                    return response
                else:
                    return {}
            finally:
                s.shutdown(socket.SHUT_RDWR)
                s.close()        

    def setPiTime(self, piTimeString):
        try:
            os.system("sudo timedatectl set-time '%s'" % piTimeString)
            self.piTime = piTimeString
        except:
            self.piTime = '?'
            self.log.warn('Failed to set Pi time')

    def waitRobot(self, maxAttempts=-1):
        robotIsReady = False
        numAttempts = 0
        while not robotIsReady:
            if maxAttempts > -1 and numAttempts >= maxAttempts:
                self.log.info("Maximum number of attempts ("+str(maxAttempts)+") to check robot status reached", True)
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
                    self.log.info('Robot not available, will check again in 3 seconds...', True)
                    time.sleep(3)

            numAttempts += 1

        return True

