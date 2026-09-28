# File which will create database and its tables

#imports
from fastapi import FastAPI
from .database import engine
from .models import Base
from .router import auth,todos,admin,users # to connect the auth file to main

# initialize FastAPI
app = FastAPI()

# testing if connection is healthy
@app.get("/check_health")
async def health_check():
    return {"status":"Healthy"}

# create all database tables mentioned inside models 
Base.metadata.create_all(bind=engine)

# routing the auth.py file with main.py file
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

