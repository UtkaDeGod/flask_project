import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm


class Category(SqlAlchemyBase):
    __tablename__ = 'categories'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)

    anecdotes = orm.relation('Anecdote', cascade="all, delete-orphan", back_populates='category')
