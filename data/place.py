import sqlalchemy
from .db_session import SqlAlchemyBase


class Place(SqlAlchemyBase):
    __tablename__ = 'places'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    opening_hours = sqlalchemy.Column(sqlalchemy.String)
    website = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    map_link = sqlalchemy.Column(sqlalchemy.String)
