import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Fun(SqlAlchemyBase):
    __tablename__ = 'funs'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    owner_id = sqlalchemy.Column(sqlalchemy.Integer)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    who_like = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=" ")

