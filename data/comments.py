import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Comment(SqlAlchemyBase):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    anecdote_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('anecdotes.id'), nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime)

    created_user = orm.relation('User')
    anecdote = orm.relation('Anecdote')