import socketserver

class ThreadedPiServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass