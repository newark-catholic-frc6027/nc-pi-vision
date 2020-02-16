import socketserver
from vision_log import Log
from pi_server_ultrasonic_service import UltrasonicService

class ClientRequestHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        self.log = Log.getInstance()
        # self.request is the TCP socket connected to the client
        self.data = str(self.request.recv(1024).decode().strip())
        self.log.debug("{} wrote:".format(self.client_address[0]))
        self.log.debug(self.data)
        commandParts = self.data.split(";")
        command = commandParts[0].strip().lower()
        if 'ultrasonic' == command:
            self.request.sendall(str.encode(str(UltrasonicService.getInstance().distance) + '\n'))
        elif 'light' == command:
            # TODO: implement light command
            print('Do light command eventually')
        else:
            self.request.sendall(self.data.upper())

        
        # TODO: add handlers for reading ultrasonic, turning on/off light
       # just send back the same data, but upper-cased
