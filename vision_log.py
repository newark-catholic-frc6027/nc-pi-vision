class Log:
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4

    LOG_LEVELS = { "trace": TRACE, "debug": DEBUG, "info": INFO, "warn": WARN, "error": ERROR}

    def __init__(self, config):
        self.logLevel = (config['Logging']['LogLevel'] or 'INFO').lower()
        self.logLevelNum = Log.LOG_LEVELS[self.logLevel]
        self.logFileCacheSize = config['Logging']['EntryCacheSize'] or 1
        self.logFileName = config['Logging']['LogFilename']
        self.logImageDir = config['Logging']['LogImageDir']


    def logFrame(self, frame, filenamePrefix, filenameSuffix):
        # TODO
        return

    def log(self, level, msg):
        # TODO
        return
        '''
        if self.logLevelNum <= level:
            # Cache the entry
            # Add timestamp
            # Add Level
            # Print to screen and/or file
            # possibly flush the cache to file
        '''

    def trace(self, msg):
        self.log(Log.TRACE, msg)

    def debug(self, msg):
        self.log(Log.DEBUG, msg)

    def info(self, msg):
        self.log(Log.INFO, msg)
    
    def warn(self, msg):
        self.log(Log.WARN, msg)

    def error(self, msg):
        self.log(Log.ERROR, msg)
