import http.server
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
from threading import Thread
import traceback

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
        # Dictionary containing lists with listeners, one list for each signal name
        self.all_listeners = dict()
        self.daemon = True
        # Dictionary with the last data for the signal names we have listeners for (so we can detect changes)
        self.listener_last_data = dict()
        self.battery_level = None
        self.temp = None
        self.data = None
        self.AC_enabled = False
        self.AC_target_temperature = 0.0
        self.start()

    def run(self):
        #Setts server to class, should listen for HTML requests
        self.server = Server(self)

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data
        self.notify_listeners()

    def get_battery_level(self):
        """
        We're assuming battery levels are in percents.
        """
        return self.data["battery_level"]

    def get_temperature(self):
        return self.temp

    def notify_listeners(self):
        # Go through all data types with listeners registered
        for data_type in self.all_listeners.keys():

            # Fetch the newest data
            data = self.data[data_type]

            # Don't notify listeners if the value hasn't changed
            if data == self.listener_last_data[data_type]:
                continue

            # Notify each listener, give them the new data
            for listener in self.all_listeners[data_type]:
                try:
                    listener(data)
                except Exception:
                    traceback.print_exc()

            # Keep track of the new data
            self.listener_last_data[data_type] = data

    def add_listener(self, listener, data_type):
        # Assume a list for this data_type already exists
        try:
            self.all_listeners[data_type].append(listener)
        except KeyError:
            # Ops, it didn't
            self.all_listeners[data_type] = [listener]
            self.listener_last_data[data_type] = None

    def remove_listener(self, listener, data_type):
        try:
            self.all_listeners[data_type].remove(listener)
        except KeyError:
            pass


"""Sets up server, must add handle methods in handler class to handle requests
"""
class Server:
    def __init__(self, status):
        def handler(*args):
            Handler(status, *args)
        httpd = HTTPServer((HOST, PORT), handler)
        httpd.serve_forever()

#Request Handler
class Handler(BaseHTTPRequestHandler):
    def __init__(self, status, *args):
        self.status = status
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_POST(self):
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode())
        message = json.dumps(self._create_response())
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(message, "utf-8"))

        self.status.set_data(data)

    def _create_response(self):
        di = {"AC_enabled": self.status.AC_enabled,
              "AC_target_temperature": self.status.AC_target_temperature}
        return di


if __name__ == "__main__":
    s = Status()
    print("Jeg var her")
