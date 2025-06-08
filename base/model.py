from sqlalchemy import Column, Integer, \
                       String, DateTime, \
                       ForeignKey, UniqueConstraint, \
                       UUID
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default='Без названия')
    author = Column(Integer, ForeignKey('users.id'))
    text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default='Not name', index=True)
    token = Column(UUID)
    login = Column(String)
    password = Column(String)

    __table_args__ = (UniqueConstraint('name', 'login'),)