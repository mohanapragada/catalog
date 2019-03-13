import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False)
    picture = Column(String(300))


class CarCompanyName(Base):
    __tablename__ = 'carcompanyname'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="carcompanyname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self.name,
            'id': self.id
        }


class CarName(Base):
    __tablename__ = 'carname'
    id = Column(Integer, primary_key=True)
    name = Column(String(350), nullable=False)
    color = Column(String(150))
    cc = Column(String(150))
    price = Column(String(10))
    cartype = Column(String(250))
    date = Column(DateTime, nullable=False)
    carcompanynameid = Column(Integer, ForeignKey('carcompanyname.id'))
    carcompanyname = relationship(
        CarCompanyName, backref=backref('carname', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User, backref="carname")

    @property
    def serialize(self):
        """Return objects data in easily serializeable formats"""
        return {
            'name': self. name,
            'color': self. color,
            'cc': self. cc,
            'price': self. price,
            'cartype': self. cartype,
            'date': self. date,
            'id': self. id
        }

engin = create_engine('sqlite:///cars.db')
Base.metadata.create_all(engin)
