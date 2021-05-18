import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy.orm import validates


class Anecdote(SqlAlchemyBase):
    __tablename__ = 'anecdotes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    category_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('categories.id'))
    rating = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    is_published = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    user = orm.relation('User')
    category = orm.relation('Category')

    comments = orm.relation("Comment", back_populates='anecdote')
    likes = orm.relation('Like', back_populates='anecdote')

    @validates("is_published")
    def validate_is_published(self, key, is_published):
        assert is_published in [0, 1, 2]
        return is_published
