from networktables import NetworkTablesInstance

class VisionDataExchanger:

        def __init__(self, serverMode=False, team='6027'):
            self.serverMode = serverMode
            self.networkTable = None
            self.team = team
            self._visionTable = None
            self._visionEntries = {}
            self._sdTable = None
            self._sdEntries = {}

        def start(self):
            # start NetworkTables
            self.networkTable = NetworkTablesInstance.getDefault()
            if self.serverMode:
                print("Startup up NetworkTables server")
                self.networkTable.startServer()
            else:
                print("Initalizing NetworkTables client for team {}".format(self.team))
                self.networkTable.startClientTeam(self.team)

            self._visionTable = self.networkTable.getTable('vision')
            self._sdTable = self.networkTable.getTable('SmartDashboard')

        def put(self, key, value):
            # First check cache for an entry.
            # If found in cache, just update the value
            # If not found in cache, create the value in the network
            #  table and cache it
            
            entry = None
            if key in self._visionEntries:
                entry = self._visionEntries[key]
                entry.setValue(value)
            else:
                self._visionTable.putValue(key, value)
                self._visionEntries[key] = self._visionTable.getEntry(key)

        def sdPut(self, key, value):
            entry = None
            if key in self._sdEntries:
                entry = self._sdEntries[key]
                entry.setValue(value)
            else:
                self._sdTable.putValue(key, value)
                self._sdEntries[key] = self._sdTable.getEntry(key)

