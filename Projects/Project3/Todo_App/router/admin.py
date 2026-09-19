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
router = APIRouter(
    # Seperate the auth and rest endpoints
    prefix='/admin',
    tags=['admin']
)

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

# API Endpoints
@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all_todos(db:db_dependency,user:user_auth):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=401,detail="Authentication Failed. Only Admin can access.")
    return db.query(Todos).all()

@router.delete("/delete_todo/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db:db_dependency,user:user_auth,todo_id:int = Path(gt=0)):
    if user is None or user.get('user_role')!='admin':
        raise HTTPException(status_code=401,detail="Authentication Failed. Only Admin can access.")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,detail="Todo not found")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()

