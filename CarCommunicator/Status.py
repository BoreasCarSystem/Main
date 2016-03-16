import http.server
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
from threading import Thread

HOST = "localhost"
PORT = 34444

class Status(Thread):
    """ We need to create a connection between this class and the CarDataStream.
    This class SHOULD listen at port 34444, where CarDataStream MUST send its data.

    Every attribute has a get-method. We've made the get-methods for battery_level and temperature, since this is
    needed for sprint 1.
    """

    def __init__(self):
        super(Status, self).__init__()
        self.all_listeners = set()
        self.battery_level = None
        self.temp = None
        self.data = None
        self.start()

    def run(self):
        #Setts server to class, should listen for HTML requests
        self.server = Server(self)

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data

    def get_battery_level(self):
        """
        We're assuming battery levels are in percents.
        """
        return self.battery_level

    def get_temperature(self):
        return self.temp

    def notify_listeners(self):
        for listener in self.all_listeners:
            listener.update()

    def add_listener(self, listener):
        self.all_listeners.add(listener)

    def remove_listener(self, listener):
        self.all_listeners.remove(listener)


"""Sets up server, must add handle methods in handler class to handle requests
"""
class Server:
    def __init__(self, status):
        def handler(*args):
            Handler(status,*args)
        httpd = HTTPServer((HOST,PORT), handler)
        httpd.serve_forever()

#Request Handler
class Handler(BaseHTTPRequestHandler):
    def __init__(self, status, *args):
        self.status = status
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode())
        self.send_response(200)
        self.end_headers()
        self.status.set_data(data)


if __name__ == "__main__":
    s = Status()
    print("Jeg var her")
