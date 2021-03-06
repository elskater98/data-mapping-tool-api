import os
from app import create_app

if __name__ == '__main__':
    # https://flask.palletsprojects.com/en/2.0.x/config/
    create_app().run(host=os.getenv('SERVER_HOSTNAME', default='127.0.0.1'), port=int(os.getenv('SERVER_PORT', default='5000')))
