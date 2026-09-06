# to create database,Session Factory and a object to access the database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

SQLALCHEMY_DB = "sqlite:///./bookvault.db"

engine = create_engine(SQLALCHEMY_DB,connect_args={'check_same_thread':False})

SessionFactory = sessionmaker(autoflush=False,autocommit=False,bind=engine)

Base = declarative_base()
