import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from data.db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String(255), unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    picture_path = sqlalchemy.Column(sqlalchemy.String(255), default='img/avatars/default.jpg')
    is_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_banned = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    anecdotes = orm.relation('Anecdote', cascade="all, delete-orphan", back_populates='user')
    comments = orm.relation('Comment', back_populates='user')
    likes = orm.relation('Like', back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
