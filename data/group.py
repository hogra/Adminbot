import sqlalchemy
import sqlalchemy.orm as orm

from .db_session import SqlAlchemyBase

# Таблица чатов в бд

class Group(SqlAlchemyBase):
    __tablename__ = 'group'
    groupid = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    words = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    pred = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=3)
    greet = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='У нас новый участник!')
    links = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=False)
    works = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    user = orm.relationship("User", back_populates='group')
