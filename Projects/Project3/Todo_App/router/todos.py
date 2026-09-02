# File to handle all API Endpoints

#imports
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, Path
from database import SessionLocal
from models import Todos
from starlette import status


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

# Pydantics requests class
class TodoRequest(BaseModel):
    title:str = Field(min_length=3)
    description:str = Field(min_length=3,max_length=100)
    priority:int = Field(gt=0,lt=6)
    complete:bool

# API endpoints
@router.get("/records")
async def get_all_records(db:db_dependency):
    return db.query(Todos).all()

# get todo by id
@router.get("/records/{todo_id}",status_code=status.HTTP_200_OK)
async def get_todo_by_id(db:db_dependency,todo_id:int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404,detail="Todo ID not found")

# create a new todo
@router.post("/create_todo",status_code=status.HTTP_201_CREATED)
async def create_todo(db:db_dependency,todo_request:TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()

# update an existing todo
@router.put("/update_todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependency,todo_updated:TodoRequest,todo_id:int=Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
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
async def delete_todo(db:db_dependency,todo_id:int=Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()