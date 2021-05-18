from flask import Flask
from flask_login import LoginManager
from data.db_session import create_session, global_init, SqlAlchemyBase
from models.users import User
from blueprints import admin_blueprint, user_blueprint, anecdotes_blueprint, jinja_filters
from api import anecdotes_resource, users_resource, comments_resource, categories_resource, likes_resource
from flask_restful import Api


def create_app(secret_key):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret_key

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

    api.add_resource(anecdotes_resource.AnecdotesResource, "/api/anecdote")
    api.add_resource(anecdotes_resource.AnecdotesListResource, "/api/anecdotes")
    api.add_resource(anecdotes_resource.AnecdotesTopResource, "/api/anecdotes/top")
    api.add_resource(anecdotes_resource.AnecdotesModerateResource, "/api/anecdotes/moderate")

    api.add_resource(users_resource.UsersListResource, "/api/users")
    api.add_resource(users_resource.UsersResource, "/api/users/<int:user_id>")
    api.add_resource(users_resource.UsersRegistrationResource, "/api/users/personal_register")

    api.add_resource(categories_resource.CategoriesResource, "/api/categories")
    api.add_resource(comments_resource.CommentsResource, "/api/comments")
    api.add_resource(likes_resource.LikesResource, "/api/likes")

    app.register_blueprint(admin_blueprint.blueprint)
    app.register_blueprint(user_blueprint.blueprint)
    app.register_blueprint(anecdotes_blueprint.blueprint)
    app.register_blueprint(jinja_filters.blueprint)

    return app


if __name__ == '__main__':
    global_init('sqlite', './db/base.db')
    app = create_app('aleksey_lox228)))')
    app.run(port=5000, host='127.0.0.2')
