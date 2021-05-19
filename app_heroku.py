from data.db_session import global_init, create_conn_args_string
from app import create_app
import os


def start_app(secret_key):
    port = int(os.environ.get('PORT', 5000))
    login = os.environ.get('LOGIN')
    password = os.environ.get('PASSWORD')
    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT')
    db_name = os.environ.get('DB_NAME')

    app = create_app(secret_key)
    global_init('mysql', create_conn_args_string(login, password, db_host, db_port, db_name))
    return app


SECRET_KEY = os.environ.get('SECRET_KEY')
app = start_app(SECRET_KEY)
