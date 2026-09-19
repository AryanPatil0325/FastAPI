# File to handle all API Endpoints

#imports
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, Path
from database import SessionLocal
from models import Todos
from starlette import status
from router.auth import get_current_user


# initialize APIRouter
router = APIRouter()

# dependency to create a new session everytime and closing it safely
def get_db():
    db = SessionLocal() # session created
    try:
        yield db
    finally:
        db.close()

# variable for loading the session and dependencies for api endpoints
db_dependency = Annotated[Session,Depends(get_db)]

# user authentication dependency to validate the jwt token
user_auth = Annotated[dict,Depends(get_current_user)]

# Pydantics requests class
class TodoRequest(BaseModel):
    title:str = Field(min_length=3)
    description:str = Field(min_length=3,max_length=100)
    priority:int = Field(gt=0,lt=6)
    complete:bool

# API endpoints
@router.get("/records")
async def get_all_records(user:user_auth,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get('user_id')).all()

# get todo by id
@router.get("/records/{todo_id}",status_code=status.HTTP_200_OK)
async def get_todo_by_id(user:user_auth,db:db_dependency,todo_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('user_id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404,detail="Todo ID not found")

# create a new todo
@router.post("/create_todo",status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_auth,db:db_dependency,todo_request:TodoRequest):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication Failed")
    todo_model = Todos(**todo_request.model_dump(),owner_id = user.get('user_id'))
    db.add(todo_model)
    db.commit()

# update an existing todo
@router.put("/update_todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user:user_auth,db:db_dependency,todo_updated:TodoRequest,todo_id:int=Path(gt=0)):
    if user is None:
            raise HTTPException(status_code=401,detail="Authentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('user_id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo ID not found")
    # update the old with new data
    todo_model.title = todo_updated.title
    todo_model.description = todo_updated.description
    todo_model.priority = todo_updated.priority
    todo_model.complete = todo_updated.complete
    # add and commit
    db.add(todo_model)
    db.commit()

# delete a todo
@router.delete("/delete_todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_auth,db:db_dependency,todo_id:int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication Failed")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get("user_id")).delete()
    db.commit()