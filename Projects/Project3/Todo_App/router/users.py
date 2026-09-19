from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, Path
from database import SessionLocal
from models import Todos,Users
from starlette import status
from router.auth import get_current_user
from passlib.context import CryptContext

# initialize APIRouter
router = APIRouter(
    # Seperate the auth and rest endpoints
    prefix='/users',
    tags=['users']
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

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

class UserVerification(BaseModel):
    existing_pass:str
    new_password:str = Field(min_length=6)

# API Endpoint
@router.get("/get_user",status_code=status.HTTP_200_OK)
async def get_all_users(db:db_dependency,user:user_auth):
    user_model = db.query(Users).filter(Users.id == user.get("user_id")).first()
    if user_model is None:
        raise HTTPException(status_code=404,detail="User not found")
    return user_model

@router.put("/change_password",status_code=status.HTTP_200_OK)
async def update_password(db:db_dependency,user:user_auth,user_verification:UserVerification):
    if user is None:
        raise HTTPException(status_code=401,detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()
    if not bcrypt_context.verify(user_verification.existing_pass,user_model.hashed_password):
        raise HTTPException(status_code=401,detail="Incorrect password or Error in password change")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    return {"message":"Password Changed Successfully"}