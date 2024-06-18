from sqlalchemy import Column, Integer, String, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .db import Base

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True)
    quote = Column(String)
    author = Column(String)
    created_at = Column(Integer)
    