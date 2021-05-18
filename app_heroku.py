from data.db_session import global_init, create_conn_args_string
from threading import Thread
from app import create_app
from bot.main import main
import asyncio
import os


async def start_app(secret_key):
    port = int(os.environ.get('PORT', 5000))
    login = os.environ.get('LOGIN')
    password = os.environ.get('PASSWORD')
    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT')
    db_name = os.environ.get('DB_NAME')

    app = create_app(secret_key)
    global_init('mysql', create_conn_args_string(login, password, db_host, db_port, db_name))
    app.run(host='127.0.0.1', port=port)


async def start_bot(token):
    main(token)


async def main_heroku():
    tasks = [asyncio.ensure_future(start_app(SECRET_KEY)), asyncio.ensure_future(start_bot(TOKEN))]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    SECRET_KEY = os.environ.get('SECRET_KEY')
    TOKEN = os.environ.get('TOKEN')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(main_heroku())


    #Thread(target=start_app, args=(SECRET_KEY,)).start()
    #Thread(target=start_bot, args=(TOKEN,)).start()
