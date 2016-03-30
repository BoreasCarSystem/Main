import requests
from Temperature import Temperature
import json
from Car import CarControl
from time import sleep
import Status
from queue import Queue

if not hasattr(json, "JSONDecodeError"):
    json.JSONDecodeError = ValueError

DEBUG = True


class Main:

    def __init__(self, car_api, port):
        self.POLLING_INTERVAL = 5
        self.car_api = car_api
        self.port = port
        self.AC_controller = None
        self.car_control = CarControl()
        self.target_temp = 20
        # Start server
        self.status = Status.Status()

        # error messages
        self.error_messages = Queue()

    def run(self):
        while True:
            self.poll()
            if DEBUG: print("Sover")
            sleep(self.POLLING_INTERVAL)

    def get_error_messages(self):
        messages = list()
        while not self.error_messages.empty():
            messages.append(self.error_messages.get_nowait())
        return messages

    def add_error_message(self, errno, debug_info, send_immediately=False):
        message = {"errno": errno, "message": debug_info}
        if send_immediately:
            self.handle(self.send_data(message, True))
        else:
            self.error_messages.put_nowait(message)

    def poll(self):
        if DEBUG: print("poller")
        data_for_server = self.status.get_data()
        # Send data if it exists
        if data_for_server is not None:
            self.handle(self.send_data(data_for_server, False))
        else:
            self.add_error_message(3, "No data")
        # Send error messages
        messages = self.get_error_messages()
        if len(messages) > 0:
            for message in messages:
                self.handle(self.send_data(message, True))

    def handle(self, r):
        print(r)
        messages = {message['type']: message['value'] for message in r}

        if 'AC_temperature' in messages:
            if DEBUG: print("Setter temperatur")
            self.target_temp = messages['AC_temperature']
            if self.AC_controller is not None:
                if DEBUG: print("oppdaterer temperatur")
                # If AC-session is started, and user wants to update temperature
                self.AC_controller.update_temperature(self.target_temp)

        if 'AC_enabled' in messages:
            if messages['AC_enabled']:
                if DEBUG: print("Temperatur aktiv, endrer temp?")
                # Activate AC by creating temperature object
                self.AC_controller = Temperature(self.car_control, self.target_temp, self, self.status)
            else:
                if self.AC_controller is not None:
                    if DEBUG: print("Deaktiverer")
                    # Deactivate AC by calling self.AC_controller.deactivate()
                    self.AC_controller.deactivate()
                    self.AC_controller = None

    def send_data(self, data, error=False):
        """
        Polls the CarAPI server for messages.

        :param error: Set to true to make this an error message for the server.
        :param data: Data to be encoded as JSON and sent to the server.
        :return: JSON returned from server
        """
        url = "http://" + self.car_api.replace("http://", "") + ":" + str(self.port)
        if error:
            url += "/error/"
        else:
            url += "/status/"

        if DEBUG: print("Sender")
        r = requests.post(url, json=data)
        if DEBUG: print("Mottatt fra server")

        r.raise_for_status()

        try:
            return r.json()
        except json.JSONDecodeError as e:
            # Could it not be decoded because there was nothing to decode?
            if len(r.content) == 0:
                # Yup, that means no messages were sent from the server
                return []
            else:
                # Nope, malformed data from server..?
                raise e


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Runs the CarCommunicator, which receives data from the car and '
                                     'acts on data from CarAPI.')
    parser.add_argument('-d', '--debug', help='Print debug messages', action="store_true")
    parser.add_argument('server_url', help="URL where carAPI can be reached.")
    parser.add_argument('server_port', default=34446, type=int, nargs="?", help="The port at which the carAPI can be reached.")
    args = parser.parse_args()
    DEBUG = args.debug
    main = Main(args.server_url, args.server_port)
    main.run()
