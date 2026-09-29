# file that holds the endpoints
from datetime import datetime, timedelta, timezone
from sqlite3 import IntegrityError
from typing import Optional,Annotated,Literal

from fastapi import APIRouter,HTTPException,Path,Query,Depends
from starlette import status
from pydantic import BaseModel, ConfigDict, EmailStr,Field

from database import SessionFactory
from sqlalchemy.orm import Session

from model import Books,Users

from passlib.context import CryptContext

from jose import jwt,JWTError

from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
# from Swagger authenticator
# from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials

import os
from dotenv import load_dotenv

router = APIRouter(
    prefix="/auth",
    tags=['auth']
)
load_dotenv()

# Swagger
# security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set in environment")

ALGORITHM = "HS256"


def get_db():
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated='auto') # used for password hashing using bcrypt

# get the JWT bearer token
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login") # endpoint which return token

oauth2pass = Annotated[OAuth2PasswordRequestForm,Depends()]


# Pydantic model for validations
class User_Request(BaseModel):
    username:str = Field(min_length=3)
    email:EmailStr # to validate the email field
    password:str = Field(min_length=5,max_length=16)
    role:Literal["user","admin"]

# Book Response class which will return the SQLAlchemy object into json
# SQLAlchemy -> pydandic model -> json 
# User Response class -> SQLalchemy to json
class User_Response(BaseModel):
    id:int
    username:str
    email:str
    role:str

    model_config = ConfigDict(from_attributes=True)

class Login_Request(BaseModel):
    username:str
    password:str

# function to create JWT token
def create_access_token(username:str,user_id:int,expiry_time:timedelta,role:str):
    encode = {"sub":username,"id":user_id, "role":role}
    expiry = datetime.now(timezone.utc) + expiry_time
    encode.update({"exp":expiry})
    return jwt.encode(encode,SECRET_KEY,algorithm=ALGORITHM)

# function to verify the token created
def verify_token(token:str):
    # handling tampered or expired tokens
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str = payload.get('sub')
        user_id: int = payload.get('id')
        role:str = payload.get('role')

        if username is None or user_id is None:
            raise HTTPException(status_code=401,detail="Couldn't verify the user")
        return {"username":username,"id":user_id,"role":role}
    except JWTError:
        raise HTTPException(status_code=401,detail="Couldn't verify the user")

# Function that gets Authentication Bearer <JWT> and extracts it 
def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    return verify_token(token)


@router.post("/create_user",status_code=status.HTTP_201_CREATED,response_model=User_Response)
async def create_new_user(db:db_dependency,new_user:User_Request):
    # users_model = Users(**new_user.model_dump())
    # hashing password
    users_model = Users(
        username = new_user.username,
        email = new_user.email,
        password = bcrypt_context.hash(new_user.password),
        role = new_user.role
    )
    # check for duplicate username and email field at database level since we are using "unique=True"
    try:
        db.add(users_model)
        db.commit()
        db.refresh(users_model)
        return users_model
        
    except IntegrityError:
        db.rollback() # reset the uncommitted state to normal to reuse it again
        raise HTTPException(status_code=409,detail="Username or Email already exists")



# 1. Receive username/email + password
#              ↓
# 2. Find the user in database
#              ↓
# 3. Get stored password hash
#              ↓
# 4. Verify supplied password against hash
#              ↓
# 5. Correct?
#        ↓              ↓
#       YES             NO
#        ↓              ↓
#   Generate JWT     Reject login



@router.post("/login")
async def create_jwt_token(db:db_dependency,credentials:oauth2pass):
    # find user in database
    user_model = db.query(Users).filter(Users.username == credentials.username).first()
    if user_model is None:
        raise HTTPException(status_code=401,detail="Invalid username or password")
    # get stored hashed
    stored_hashed = user_model.password
    if bcrypt_context.verify(credentials.password,stored_hashed):
        # generate JWT
        token = create_access_token(credentials.username,user_model.id,timedelta(minutes=20),user_model.role)
        # return token
        return {"access_token":token,"token_type":"bearer"}
        
    else:
        raise HTTPException(status_code=401,detail='Invalid username or password')

   
