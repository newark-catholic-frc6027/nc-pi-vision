from networktables import NetworkTablesInstance
import time

class VisionDatahub:

        def __init__(self, serverMode=False, team='6027'):
            self.serverMode = serverMode
            self.networkTable = None
            self.team = team
            self._visionTable = None
            self._visionEntries = {}
            self._sdTable = None
            self._sdEntries = {}
            self.networkTableConnected = False

        def start(self):
            # start NetworkTables
            self.networkTable = NetworkTablesInstance.getDefault()
            if self.serverMode:
                print("Startup up NetworkTables server")
                self.networkTable.startServer()
            else:
                print("Initalizing NetworkTables client for team {}".format(self.team))
                self._ensureConnected(20)
            #end if

            self._visionTable = self.networkTable.getTable('vision')
            self._sdTable = self.networkTable.getTable('SmartDashboard')

        def put(self, keyOrDict, value=None):
            self._ensureConnected()

            if type(keyOrDict) is dict:
                for key, value in keyOrDict.items():
                    self.put(key, value)
                # end for
                return
                
            # First check cache for an entry.
            # If found in cache, just update the value
            # If not found in cache, create the value in the network
            #  table and cache it
            key = keyOrDict # Must have a key at this point
            entry = None
            if key in self._visionEntries:
                entry = self._visionEntries[key]
                entry.setValue(value)
            else:
                self._visionTable.putValue(key, value)
                self._visionEntries[key] = self._visionTable.getEntry(key)

        def sdPut(self, key, value):
            self._ensureConnected()
            entry = None
            if key in self._sdEntries:
                entry = self._sdEntries[key]
                entry.setValue(value)
            else:
                self._sdTable.putValue(key, value)
                self._sdEntries[key] = self._sdTable.getEntry(key)

        def _ensureConnected(self, maxAttempts=1):
            if not self.serverMode and not self.networkTableConnected:
                self.networkTable.startClientTeam(self.team)
                self.networkTableConnected = self.networkTable.isConnected()
                if self.networkTableConnected:
                    print("NetworkTables CONNECTED!")
                else:
                    if maxAttempts > 1:
                        attemptCount = 1
                        while (not self.networkTableConnected and attemptCount <= maxAttempts):
                            time.sleep(1)
                            self.networkTable.startClientTeam(self.team)
                            self.networkTableConnected = self.networkTable.isConnected()
                            attemptCount += 1
                        #end while
                        if not self.networkTableConnected:
                            print(">> WARN >> NetworkTables NOT CONNECTED")
                        else:
                            print("NetworkTables CONNECTED after %d attempts!" % attemptCount)
                    #end if


