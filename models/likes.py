import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy.orm import validates


class Like(SqlAlchemyBase):
    __tablename__ = 'likes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    anecdote_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('anecdotes.id'), nullable=False)
    value = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    user = orm.relation('User')
    anecdote = orm.relation('Anecdote')

    @validates("value")
    def validate_value(self, key, value):
        assert value in [-1, 0, 1]
        return value
