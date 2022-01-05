# data-mapping-tool-api

### Run Server

        flask run --host=localhost --port=3000

### Generate Secret Key

    $ python -c 'import secrets; print(secrets.token_hex())'
    '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'

### .ENV

    FLASK_APP=app
    FLASK_ENV=[development | production]
    
    SECRET_KEY=
    SERVER_HOSTNAME=
    SERVER_PORT=
    
    JWT_SECRET_KEY=
    JWT_ACCESS_TOKEN_EXPIRES=
    JWT_REFRESH_TOKEN_EXPIRES=