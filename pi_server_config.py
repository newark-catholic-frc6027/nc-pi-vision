import sys
import configparser
import os.path

class PiServerConfig:

    DEFAULT_CONFIG_FILENAME = "./pi_server_cfg.ini"

    def __init__(self, piServerConfigFilename=None):
        self.serverConfigFilename = piServerConfigFilename or PiServerConfig.DEFAULT_CONFIG_FILENAME
        self.config = None


    def readConfig(self):
        self.config = configparser.ConfigParser()
        if self.serverConfigFilename and os.path.isfile(self.serverConfigFilename):
            try:
                self.config.read(self.serverConfigFilename)
            except:
                print("Server config file not found at '{}': {}".format(self.serverConfigFilename, sys.exc_info()[0]))

