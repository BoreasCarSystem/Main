import requests
from Temperature import Temperature
from json import JSONDecodeError
from Car import CarControl
from time import sleep


class Main:

    def __init__(self, car_api, port):
        self.POLLING_INTERVAL = 20
        self.car_api = car_api
        self.port = port
        self.AC_controller = None
        self.car_control = CarControl()
        self.target_temp = 20

    def run(self):
        while True:
            self.poll()
            sleep(self.POLLING_INTERVAL)

    def poll(self):
        # TODO: Send fresh car information to the server
        self.handle(self.send_data(self.get_error_message(), True))

    def handle(self, r):
        messages = {message['type']: message['value'] for message in r}

        if 'AC_temperature' in messages:
            self.target_temp = messages['AC_temperature']
            if self.AC_controller is not None:
                # If AC-session is started, and user wants to update temperature
                self.AC_controller.update_temperature(self.target_temp)

        if 'AC_enabled' in messages:
            if messages['AC_enabled']:
                # Activate AC by creating temperature object
                self.AC_controller = Temperature(self.car_control, self.target_temp)
            else:
                if self.car_control is not None:
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
        r = requests.post(url, json=data)
        r.raise_for_status()

        try:
            return r.json()
        except JSONDecodeError as e:
            # Could it not be decoded because there was nothing to decode?
            if len(r.content) == 0:
                # Yup, that means no messages were sent from the server
                return []
            else:
                # Nope, malformed data from server..?
                raise e

    def get_error_message(self):
        """
        Return JSON-compatible object, placeholder since we don't
        have car data to send yet.
        :return:
        """
        return {"errno": 3, "message": "Not implemented yet"}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Runs the CarCommunicator, which receives data from the car and '
                                     'acts on data from CarAPI.')
    parser.add_argument('server_url', help="URL where carAPI can be reached.")
    parser.add_argument('server_port', default=34446, type=int, nargs="?", help="The port at which the carAPI can be reached.")
    args = parser.parse_args()
    main = Main(args.server_url, args.server_port)
    main.run()
