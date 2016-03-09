import requests
from Temperature import Temperature




class Main:

    def __init__(self, car_api, port):
        self.car_api = car_api
        self.port = port

    def run(self):
        r = self.send_data(self.get_error_message(), True)
        print(r)

    def send_data(self, data, error=False):
        """
        Polls the CarAPI server for messages.
        :param data: Data to be encoded as JSON and sent to the server.
        :return: JSON returned from server
        """
        url = "http://" + self.car_api.replace("http://", "") + ":" + str(self.port)
        if error:
            url += "/error/"
        else:
            url += "/status/"
        r = requests.post(url, json=data)
        return r

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
