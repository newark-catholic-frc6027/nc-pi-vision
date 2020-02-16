import socketserver
import threading
import atexit
import sys
import time

from vision_log import Log
from pi_server_config import PiServerConfig
from pi_threaded_server import ThreadedPiServer
from pi_server_client_request_handler import ClientRequestHandler
from pi_server_ultrasonic_service import UltrasonicService

# GLOBALS
onExitInvoked = False
log = None

def onExit():
    global onExitInvoked
    global log

    UltrasonicService.getInstance().stop()

    if onExitInvoked:
        return

    onExitInvoked = True
    if log:
        log.info("Exiting pi_server", True)
    else:
        print("Exiting pi_server main")

if __name__ == "__main__":

    try:
        atexit.register(onExit)
        configFile = None
        if len(sys.argv) >= 3:
            if '-cfg' in sys.argv:
                configFile = sys.argv[sys.argv.index('-cfg') + 1]

        piServerConfig = PiServerConfig(configFile)
        piServerConfig.readConfig()
        config = piServerConfig.config

        log = Log.getInstance(config)

        host, port = '', int(config['Server']['Port']) #config['Server']['Host'], int(config['Server']['Port']) #"localhost", 9999

        log.info("Starting server on port %d" % port)
        server = ThreadedPiServer((host, port), ClientRequestHandler)

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        log.info("Server running in thread: %s" % server_thread.name)

        # Startup Ultrasonic service
        log.info("Starting ultrasonic service...")
        UltrasonicService.getInstance().startup()
        log.info("Ultrasonic service started")

        doExit = False
        while not doExit:
            try:
                time.sleep(.5)
            except KeyboardInterrupt:
                server.shutdown()
                server.server_close()
                server = None
                doExit = True

    except:  # catch any error
        if log:
            log.error("Unexpected error: "+ str(sys.exc_info()[0]))
        else:
            print("Unexpected error: "+ str(sys.exc_info()[0]))

        raise   # rethrow the error
    finally:
        if server:
             server.shutdown()
             server.server_close()

        onExit()