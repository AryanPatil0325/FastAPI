# File which will create database and its tables

#imports
from fastapi import FastAPI, Request
from .database import engine
from .models import Base
from .router import auth,todos,admin,users # to connect the auth file to main
# for frontend 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# initialize FastAPI
app = FastAPI()


# create all database tables mentioned inside models 
Base.metadata.create_all(bind=engine)

# frontend
templates = Jinja2Templates(directory="Todo_App/templates")

# mount the static files (css/js) into html
app.mount("/static",StaticFiles(directory="Todo_App/static"),name="static")

# testing if connection is healthy
@app.get("/check_health")
async def health_check():
    return {"status":"Healthy"}

# endpoint to load the html file and return a Request type
@app.get("/")
def test(request:Request):
    return templates.TemplateResponse(
        name="home.html",
        request=request,
        context={"request":request},
        status_code=200
        )

# routing the auth.py file with main.py file
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

