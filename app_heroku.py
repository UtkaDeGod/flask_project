from blueprints import admin_blueprint, user_blueprint, anecdotes_blueprint
from data.db_session import global_init
from app import app
import os


if __name__ == '__main__':
    global_init('db/anecdotes.db')
    app.register_blueprint(admin_blueprint.blueprint)
    app.register_blueprint(user_blueprint.blueprint)
    app.register_blueprint(anecdotes_blueprint.blueprint)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)