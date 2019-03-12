import datetime
class Log:
    TRACE = 0
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4

    LOG_LEVELS = { "trace": TRACE, "debug": DEBUG, "info": INFO, "warn": WARN, "error": ERROR}
    LOG_LEVEL_NAMES = { TRACE: "TRACE", DEBUG: "DEBUG", INFO: "INFO", WARN: "WARN", ERROR: "ERROR"}

    instance = None

    @staticmethod
    def getInstance(config=None):
        if Log.instance is None:
            Log.instance = Log(config)
        
        return Log.instance

    def __init__(self, config):
        self.logLevel = (config['Logging']['LogLevel'] or 'INFO').lower()
        self.logLevelNum = Log.LOG_LEVELS[self.logLevel]
        try:
            self.logFileCacheSize = int(config['Logging']['EntryCacheSize']) or 1
        except:
            self.logFileCacheSize = 1
        try:
            self.logFilename = config['Logging']['LogFilename']
        except KeyError:
            self.logFilename = None
            
        self.logImageDir = config['Logging']['LogImageDir']
        self.entryCount = 0
        self.cache = []


    def logFrame(self, frame, filenamePrefix, filenameSuffix):
        # TODO
        return

    def log(self, level, msg, flush=False):
        if self.logLevelNum > level:
            return

        timestamp = datetime.datetime.now().strftime("%m-%d %H.%M.%S.%f")[:-3]
        msg = "{} [{}] - {}".format(timestamp, Log.LOG_LEVEL_NAMES[level], msg)
        print(msg)
        if self.logFilename:
            self.cache.append(msg)
            self.entryCount += 1
            if flush or self.entryCount >= self.logFileCacheSize:
                self._flushCache()

    def trace(self, msg, flush=False):
        self.log(Log.TRACE, msg, flush)

    def debug(self, msg, flush=False):
        self.log(Log.DEBUG, msg, flush)

    def info(self, msg, flush=False):
        self.log(Log.INFO, msg, flush)
    
    def warn(self, msg, flush=False):
        self.log(Log.WARN, msg, flush)

    def error(self, msg, flush=False):
        self.log(Log.ERROR, msg, flush)

    def _flushCache(self):
        file = open(self.logFilename, 'a+')
        file.write('\n'.join(self.cache))
        file.flush()
        file.close()
        self.entryCount = 0
