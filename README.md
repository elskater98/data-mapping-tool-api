# Data Mapping Tool

This repository is the `backend` part of the Data Mapping Tool Project.

The project aims to make friendly the process of mapping data using a single ontology or multiple ones. In our case, the
project uses the [BIGG](https://www.bigg-project.eu/) ontology as background.

# Getting Started

## Prerequisite

- Python 3.8+ 🐍
- MongoDB

If you do not have a MongoDB, you can deploy it using `docker-compose up -d`.

## Install Python Dependencies

    pip install -r requirements.txt

## Run Server

    flask run --host=[localhost] --port=[port]

## File Format: .env

    FLASK_APP=app
    FLASK_ENV=[development | production]
    
    SECRET_KEY=
    SERVER_HOSTNAME=
    SERVER_PORT=
    
    JWT_SECRET_KEY=
    JWT_ACCESS_TOKEN_EXPIRES=
    JWT_REFRESH_TOKEN_EXPIRES=

    UPLOAD_FOLDER=

    MONGO_URI=

### ¿ How to Generate Secret Key ?

    $ python -c 'import secrets; print(secrets.token_hex())'
    '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'