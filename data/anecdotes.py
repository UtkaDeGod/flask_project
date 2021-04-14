import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Anecdote(SqlAlchemyBase):
    __tablename__ = 'anecdotes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('categories.id'), nullable=False)
    rating = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_published = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    created_user = orm.relation('User')
    category = orm.relation('Category')

    comments = orm.relation("Comment", back_populates='anecdote')