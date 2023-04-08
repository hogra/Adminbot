from .db_session import SqlAlchemyBase
import sqlalchemy
import sqlalchemy.orm as orm


class Group(SqlAlchemyBase):
    __tablename__ = 'group'
    groupid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    keys = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    works = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    user = orm.relationship("User", back_populates='group')