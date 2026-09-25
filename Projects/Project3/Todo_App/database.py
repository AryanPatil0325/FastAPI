# Used to connect FastAPI application with the Database using SQL lite

# imports
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# path to database link
SQLALCHEMY_DATABASE_URL = "sqlite:///./todosApp.db" # sqlite3 database 
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:aryan03@127.0.0.1:3306/todoapplicationdatabase" # mysql database 

# creating engine of database to connect 
# engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={'check_same_thread':False}) # use multiple-threads to check connection (for sqlite3)
engine = create_engine(SQLALCHEMY_DATABASE_URL) # for mysql

# create session factory for sessions 
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

# create a base object of the database for future data tables
Base = declarative_base()