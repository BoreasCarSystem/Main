# PI
System for collecting car data and communicating with the CarAPI server.

## Setup
1. Clone this repository
2. Open a terminal, and navigate inside the repository
3. Follow a tutorial ([like this one](http://docs.python-guide.org/en/latest/dev/virtualenvs/)) on how to set up virtualenv. 
Remember to use Python 3.4.
4. Active the virtualenv. Assuming you named the folder venv, run `source venv/bin/activate`
4. Run `pip install -r requirements.txt`

## How to run

1. See BoreasCarSystem/CarAPI and set up and start the server.
2. Run `CarCommunicator/Main.py`.
2. To simulate car data, run `CarDataStream/DataStream.py`.

Use the `--help` option to see available options and arguments, both optional and required.
