import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Like(SqlAlchemyBase):
    __tablename__ = 'likes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    anecdote_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('anecdotes.id'), nullable=False)
    value = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    user = orm.relation('User')
    anecdote = orm.relation('Anecdote')
