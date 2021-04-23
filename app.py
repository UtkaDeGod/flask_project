from flask import Flask
from flask_login import LoginManager
from data.db_session import *
from models.users import User
from blueprints import admin_blueprint, user_blueprint, anecdotes_blueprint
from data import anecdotes_resource
from flask_restful import Api

app = Flask(__name__)
app.config['SECRET_KEY'] = 'aleksey_lox))))_228'

api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = create_session()
    user = db_sess.query(User).get(user_id)
    if user is None or not user.is_banned:
        return user
    return None


api.add_resource(anecdotes_resource.AnecdotesResource, "/anecdote")
api.add_resource(anecdotes_resource.AnecdotesListResource, "/anecdotes/page")
api.add_resource(anecdotes_resource.AnecdotesTopResource, "/anecdotes/top")

if __name__ == '__main__':
    global_init('db/anecdotes.db')
    app.register_blueprint(admin_blueprint.blueprint)
    app.register_blueprint(user_blueprint.blueprint)
    app.register_blueprint(anecdotes_blueprint.blueprint)
    app.run(port=5000, host='127.0.0.2')
