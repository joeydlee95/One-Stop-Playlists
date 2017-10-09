import os
import sys
import datetime
import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Playlist(Base):
    __tablename__ = 'playlist'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    timestamp = Column(DateTime, default=sqlalchemy.func.current_timestamp())
    description = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
        }


class SongItem(Base):
    __tablename__ = 'song_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    link = Column(String(250))
    genre = Column(String(80), nullable=False)
    playlist_id = Column(Integer, ForeignKey('playlist.id'))
    playlist = relationship(Playlist)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'link': self.link,
            'id': self.id,
            'genre': self.genre,
        }


engine = create_engine('sqlite:///playlist.db')


Base.metadata.create_all(engine)
