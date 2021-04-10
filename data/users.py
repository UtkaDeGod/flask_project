import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    picture_path = sqlalchemy.Column(sqlalchemy.String, default='pic_path.png')

    anecdotes = orm.relation('Anecdote', back_populates='created_user')
    comments = orm.relation('Comment', back_populates='comment')
    likes = orm.relation('Like', back_populates='user')
