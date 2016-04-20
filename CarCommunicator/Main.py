import requests
import requests.exceptions
from Temperature import Temperature
import json
from Car import CarControl
from time import sleep
import Status
from queue import Queue
import traceback

# Backwards-compatible for python < 3.5
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
        self.target_time = None

        # Start server
        self.status = Status.Status()

        # error messages
        self.error_messages = Queue()

    def run(self):
        while True:
            self._poll()
            self._set_ac_status_in_status()
            if DEBUG: print("Sover")
            sleep(self.POLLING_INTERVAL)

    def _get_error_messages(self):
        messages = list()
        while not self.error_messages.empty():
            messages.append(self.error_messages.get_nowait())
        return messages

    def add_error_message(self, errno, debug_info):
        message = {"errno": errno, "message": debug_info}
        self.error_messages.put(message)

    def _poll(self):
        try:
            if DEBUG: print("poller")
            data_for_server = self._get_data_for_server()
            # Send data if it exists
            if data_for_server is not None:
                self._handle(self._send_data(data_for_server, False))
            else:
                self.add_error_message(3, "No data")
            # Send error messages
            messages = self._get_error_messages()
            if len(messages) > 0:
                for message in messages:
                    self._handle(self._send_data(message, True))
        except requests.exceptions.RequestException:
            traceback.print_exc()
            return []

    def _handle(self, r):
        print(r)
        messages = {message['type']: message['value'] for message in r}

        if 'AC_temperature' in messages:
            if DEBUG: print("Setter temperatur")
            self.target_temp = messages['AC_temperature']
            if self.AC_controller is not None:
                if DEBUG: print("oppdaterer temperatur")
                # If AC-session is started, and user wants to update temperature
                self.AC_controller.update_temperature(self.target_temp)

        if "AC_timer" in messages:
            if self.AC_controller is not None:
                self.AC_controller.deactivate()
                messages["AC_enabled"] = True
            if DEBUG: print("Setter tidspunkt")
            self.target_time = messages["AC_timer"]

        if 'AC_enabled' in messages and (self.AC_controller is not None) != (messages['AC_enabled']):
            if messages['AC_enabled']:
                if DEBUG: print("Setter på AC (evt. timer)")
                # Activate AC by creating temperature object
                self.AC_controller = Temperature(self.car_control, self.target_temp, self, self.status, self.target_time)
            else:
                if self.AC_controller is not None:
                    if DEBUG: print("Deaktiverer")
                    # Deactivate AC
                    self.AC_controller.deactivate()

    def _get_data_for_server(self):
        # Make a copy of the status data
        try:
            data = dict(self.status.get_data())

            # Add AC control stuff
            data['AC_enabled'] = self.AC_controller is not None
            data['AC_temperature'] = self.target_temp
            data['AC_time'] = self.target_time
            return data
        except TypeError:
            return None

    def _set_ac_status_in_status(self):
        self.status.AC_enabled = self.car_control.AC_enabled
        self.status.AC_target_temperature = self.car_control.AC_target_temperature

    def _send_data(self, data, error=False):
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
