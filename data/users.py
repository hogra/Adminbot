import sqlalchemy
import sqlalchemy.orm as orm

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    userid = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    groupid = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("group"))  # foreign key = true
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pred = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=True)
    group = orm.relationship("Group", back_populates='user')
