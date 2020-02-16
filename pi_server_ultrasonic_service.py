import threading
import time
from vision_log import Log
import hazelcast

class UltrasonicService:
    instance = None

    log = None

    stopped = False
    distance = -1.0
    hzClient = None
    topic = None

    @staticmethod
    def getInstance():
        if UltrasonicService.instance is None:
            UltrasonicService.instance = UltrasonicService()
        
        return UltrasonicService.instance

    def __init__(self):
        self.log = Log.getInstance()

    def startup(self):
        config = hazelcast.ClientConfig()
        config.group_config.name = 'robot'
        networkConfig = config.network_config
        networkConfig.addresses.append("192.168.254.99:5806") # pi address
        self.hzClient = hazelcast.HazelcastClient(config)
        self.topic = self.hzClient.get_topic("ultrasonic")

        t1 = threading.Thread(target=self.readUltrasonicDataUntilStopped)
        t1.start()

    def stop(self):
        self.stopped = True
        self.hzClient.shutdown()

    def readUltrasonicDataUntilStopped(self):
        # TODO: add code to continually read ultrasonic until self.stopped == True
        # and update lastDistance
        self.log.debug('readUltrasonicDataUntilStopped entered')
        while not self.stopped:
            # Do code to read ultrasonic here
            
            # remove these lines of code once above code is in
            self.topic.publish(self.distance)
            self.log.info("Published distance: " + str(self.distance))
            self.distance += 1.0
            
            time.sleep(.5)


        self.log.info('UltrasonicService stopped')
            
