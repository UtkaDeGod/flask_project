from data.db_session import global_init, create_conn_args_string
from threading import Thread
from app import create_app
from bot.main import main
import os


def start_app(secret_key):
    port = int(os.environ.get('PORT', 5000))
    login = os.environ.get('LOGIN')
    password = os.environ.get('PASSWORD')
    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT')
    db_name = os.environ.get('DB_PORT')

    global_init('mysql', create_conn_args_string(login, password, db_host, db_port, db_name))
    app = create_app(secret_key)
    app.run(host='0.0.0.0', port=port)


def start_bot(token):
    main(token)


if __name__ == '__main__':
    SECRET_KEY = os.environ.get('SECRET_KEY')
    TOKEN = os.environ.get('TOKEN')

    Thread(target=start_app, args=(SECRET_KEY,)).start()
    Thread(target=start_bot, args=(TOKEN,)).start()
