# File which will create database and its tables

#imports
from fastapi import FastAPI
from database import engine
import models
from router import auth,todos,admin,users # to connect the auth file to main

# initialize FastAPI
app = FastAPI()

# create all database tables mentioned inside models 
models.Base.metadata.create_all(bind=engine)

# routing the auth.py file with main.py file
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

