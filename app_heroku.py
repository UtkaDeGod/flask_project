from data.db_session import global_init
from threading import Thread
from app import create_app
from bot.main import main
import os


def start_app(secret_key):
    global_init('db/anecdotes.db')
    app = create_app(secret_key)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


def start_bot(token):
    main(token)


if __name__ == '__main__':
    SECRET_KEY = os.environ.get('SECRET_KEY')
    TOKEN = os.environ.get('TOKEN')

    Thread(target=start_app, args=(SECRET_KEY,)).start()
    Thread(target=start_app, args=(TOKEN,)).start()
