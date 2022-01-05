from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    # https://flask.palletsprojects.com/en/2.0.x/config/
    app.run(host=os.getenv('SERVER_HOSTNAME', default='localhost'), port=int(os.getenv('SERVER_PORT', default='8080')))
