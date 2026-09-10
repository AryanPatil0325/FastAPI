# File to handle authentication and authorization 

#imports
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import SessionLocal
from starlette import status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer # to decode the JWT 
from jose import JWTError, jwt


# instance
router = APIRouter(
    # Seperate the auth and rest endpoints
    prefix='/auth',
    tags=['auth']
)
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

# JWT Secret and Algorithm
SECRET_KEY = "firstfastapisecret12345"
ALGORITHM = "HS256"

# Class for user creation
class UserRequest(BaseModel):
    email:str
    username:str
    first_name:str
    last_name:str
    password:str
    role:str

# Token class to validate the response of token
class Token(BaseModel):
    access_token:str
    token_type : str

# dependency function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# dependency injection
db_dependency = Annotated[Session,Depends(get_db)]

# OAuth2PasswordRequestForm dependency injection
pass_dependency = Annotated[OAuth2PasswordRequestForm,Depends()]

# OAuth2PasswordBearer Dependency Injection to retrieve and validate the URL passed by user
oauth2bearer = OAuth2PasswordBearer(tokenUrl='auth/token') # token is like an endpoint "/token"

# Authenticate Users
def authenticate_users(username:str, password:str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user

# to create access token to authorize 
def create_access_token(username:str,user_id:int,expires_delta:timedelta):
    encode_dict = {'sub':username,'id':user_id}
    expire_time = datetime.now(timezone.utc) + expires_delta
    encode_dict.update({'exp':expire_time})
    return jwt.encode(encode_dict,SECRET_KEY,algorithm=ALGORITHM)

# function to decode the JWT token and used in that endpoint where the JWT token is generated
async def get_current_user(token:Annotated[str,Depends(oauth2bearer)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        username:str = payload.get('sub') # encode_dict = {'sub':username,'id':user_id}
        user_id:int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate user")
        return {'username':username,'user_id':user_id}
    except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate user")


# authentication endpoints

# Create user 
@router.post("/auth_create_user",status_code=status.HTTP_201_CREATED)
async def create_new_user(db:db_dependency,create_user:UserRequest):
    # create_user_model = Users(**create_users.model_dump()) not useful as we have password in UserRequest and hashed_password in Users model
    create_user_model = Users(
        email = create_user.email,
        username = create_user.username,
        first_name = create_user.first_name,
        last_name = create_user.last_name,
        hashed_password = bcrypt_context.hash(create_user.password),
        role = create_user.role,
        is_active = True
    )
    db.add(create_user_model)
    db.commit()

# user authentication endpoint token with JWT Authorization
@router.post("/token",response_model=Token)
async def login_for_access_token(form_data:pass_dependency,db:db_dependency):
    # validate the incoming data with stored data in database
    user = authenticate_users(form_data.username,form_data.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate user")
    token = create_access_token(user.username,user.id,timedelta(minutes=20))
    return {"access_token":token,"token_type":"bearer"}