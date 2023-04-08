from .db_session import SqlAlchemyBase
import sqlalchemy
import sqlalchemy.orm as orm

class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    userid = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    groupid = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("group")) # foreign key = true
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    status = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    group = orm.relationship("Group", back_populates='user')