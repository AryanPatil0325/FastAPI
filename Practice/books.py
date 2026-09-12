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

from fastapi.security import OAuth2PasswordBearer
# from Swagger authenticator
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials

router = APIRouter()

# Swagger
security = HTTPBearer()

SECRET_KEY = "aryan"
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
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="login") # endpoint which return token

# Pydantic model for validations
class Book_Request(BaseModel):
    # id:Optional[int] = Field(description="ID field is not required",default=None)
    title:str = Field(min_length=3,max_length=100)
    author:str = Field(min_length=3)
    category:str = Field(min_length=3)
    price:int = Field(gt=0)
    # owner_id:int = Field(gt=0)

class User_Request(BaseModel):
    username:str = Field(min_length=3)
    email:EmailStr # to validate the email field
    password:str = Field(min_length=5,max_length=16)
    role:Literal["user","admin"]

# Book Response class which will return the SQLAlchemy object into json
# SQLAlchemy -> pydandic model -> json 
class Book_Response(BaseModel):
    id:int
    title:str 
    author:str
    category:str 
    price:int 
    owner_id:int

    # convert the SQLalchemy object into pydantic
    model_config = ConfigDict(from_attributes=True)

# User Response class -> SQLalchemy to json
class User_Response(BaseModel):
    id:int
    username:str
    email:str
    role:str

    model_config = ConfigDict(from_attributes=True)

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
# def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
#     return verify_token(token)

# Swagger credentials
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    token = credentials.credentials
    return verify_token(token)

# authentication dependency to check for valid jwt
auth_dependency = Annotated[dict,Depends(get_current_user)]


# List of books
# Books = [
#     {
#         "id": 1,
        # "title": "Atomic Habits",
        # "author": "James Clear",
        # "category": "Self-Help",
        # "price": 499,
        # "owner_id": 1
#     },
#     {
#         "id": 2,
        # "title": "The Alchemist",
        # "author": "Paulo Coelho",
        # "category": "Fiction",
        # "price": 299,
        # "owner_id": 2
#     },
#     {
#         "id": 3,
        # "title": "Clean Code",
        # "author": "Robert C. Martin",
        # "category": "Programming",
        # "price": 799,
        # "owner_id": 1
#     },
#     {
#         "id": 4,
#         "title": "Deep Work",
#         "author": "Cal Newport",
#         "category": "Productivity",
#         "price": 450,
#         "owner_id": 3
#     },
#     {
#         "id": 5,
#         "title": "Harry Potter and the Philosopher's Stone",
#         "author": "J.K. Rowling",
#         "category": "Fantasy",
#         "price": 599,
#         "owner_id": 2
#     },
    # {
    #     "id": 6,
    #     "title": "The Psychology of Money",
    #     "author": "Morgan Housel",
    #     "category": "Finance",
    #     "price": 399,
    #     "owner_id": 3
    # },
#     {
#         "id": 7,
#         "title": "Python Crash Course",
#         "author": "Eric Matthes",
#         "category": "Programming",
#         "price": 699,
#         "owner_id": 1
#     },
#     {
#         "id": 8,
#         "title": "Ikigai",
#         "author": "Hector Garcia",
#         "category": "Self-Help",
#         "price": 299,
#         "owner_id": 2
#     }
# ]

@router.get("/books",status_code=status.HTTP_200_OK,response_model = list[Book_Response]) # Response model is for single book but we are getting multiple books in list
async def get_all_books(
    db:db_dependency,
    current_user:auth_dependency,
    author:Optional[str]=Query(None,min_length=3),
    category:Optional[str]=Query(None,min_length=3),
    limit:Optional[int]=Query(None,gt=0,lt=21)
    ):
    # check for user role
    if current_user.get('role').casefold() == "admin":
        filtered_books = db.query(Books)
        
        if author is not None:
            # filtered_books = [book for book in filtered_books if book.get('author').casefold() == author.casefold()]
            filtered_books = filtered_books.filter(Books.author.ilike(author.casefold()))
        
        if category is not None:
            # filtered_books = [book for book in filtered_books if book.get('category').casefold() == category.casefold()]
            filtered_books = filtered_books.filter(Books.category.ilike(category.casefold()))

        if limit is not None:
            # filtered_books = filtered_books[:limit]
            filtered_books = filtered_books.limit(limit)

        book_query = filtered_books.all()

        if not book_query: # checks for empty result
            raise HTTPException(status_code=404,detail='Book not found')

        return book_query

    elif current_user.get('role').casefold() == 'user':
        filtered_books = db.query(Books).filter(Books.owner_id == current_user.get('id'))
        if author is not None:
            # filtered_books = [book for book in filtered_books if book.get('author').casefold() == author.casefold()]
            filtered_books = filtered_books.filter(Books.author.ilike(author.casefold()))
                
        if category is not None:
            # filtered_books = [book for book in filtered_books if book.get('category').casefold() == category.casefold()]
            filtered_books = filtered_books.filter(Books.category.ilike(category.casefold()))
        
        if limit is not None:
            # filtered_books = filtered_books[:limit]
            filtered_books = filtered_books.limit(limit)
        
        book_query = filtered_books.all()
        
        if not book_query: # checks for empty result
            raise HTTPException(status_code=404,detail='Book not found')
        
        return book_query
    
    else:
        raise HTTPException(status_code=403,detail="Role not allowed")

    

@router.post("/new_book",status_code=status.HTTP_201_CREATED,response_model=Book_Response)
async def create_new_book(db:db_dependency,current_user:auth_dependency,new_book:Book_Request):
    book_model = Books(**new_book.model_dump(),owner_id = current_user.get('id'))
    db.add(book_model)
    db.commit()
    db.refresh(book_model)
    return book_model

# @router.put("/update_book/",status_code=status.HTTP_200_OK)
# async def update_book(db:db_dependency,updated_book:Book_Request,id:int=Query(gt=0)):
#     for index,book in enumerate(Books):
#         if book.get('id') == id:
#             # to handle the data integrity part -> id = id but what if passed id in data is greater than existing -> it will change the existing data
#             updated_book = updated_book.model_dump()
#             updated_book['id'] = book['id'] # If the ID inside the request body is 99, it gets replaced with the existing book's ID 1.
#             Books[index] = updated_book
#             return{"message":"Book updated successfully"}
#     raise HTTPException(status_code=404,detail="ID not found")

@router.put("/update_book/",status_code=status.HTTP_200_OK,response_model=Book_Response)
async def update_book(db:db_dependency,current_user:auth_dependency,updated_book:Book_Request,id:int=Query(gt=0)):
    book_model = db.query(Books).filter(Books.id == id).first()
    if book_model is None:
        raise HTTPException(status_code=404,detail="ID not found")

# Authorizing the user only who is authenticated & Role = Admin ->any book , user -> should match with current user id
    if current_user.get('role').casefold() == 'admin':
        book_model.title = updated_book.title
        book_model.author = updated_book.author
        book_model.category = updated_book.category
        book_model.price = updated_book.price
        db.commit()
        return book_model
    elif current_user.get('role').casefold() == 'user':
        if book_model.owner_id == current_user.get('id'):
            book_model.title = updated_book.title
            book_model.author = updated_book.author
            book_model.category = updated_book.category
            book_model.price = updated_book.price
            # book_model.owner_id = updated_book.owner_id
            db.commit()
            return book_model
        else:
            raise HTTPException(status_code=403,detail="Action Is Forbidden")
    else:
        raise HTTPException(status_code=403,detail='Role not found')

# @router.delete("/delete_book/{book_id}",status_code=status.HTTP_200_OK)
# async def delete_book(book_id:int=Path(gt=0)):
#     for index,book in enumerate(Books):
#         if book.get('id') == book_id:
#             Books.remove(book)
#             return {"message":"Book deleted successfully"}
#     raise HTTPException(status_code=404,detail="Book not found")

@router.delete("/delete_book/{book_id}",status_code=status.HTTP_200_OK)
async def delete_book(db:db_dependency,current_user:auth_dependency,book_id:int=Path(gt=0)):
    book_model = db.query(Books).filter(Books.id == book_id).first()
    if book_model is None:
        raise HTTPException(status_code=404,detail="ID not found")

    # Admin - delete any book , user -> check the authenticated user id
    if current_user.get('role').casefold() == 'admin':
        db.delete(book_model)
        db.commit()
        return{"message":"Book deleted successfully"}
    elif current_user.get('role').casefold() == 'user':
        if book_model.owner_id == current_user.get('id'):
            db.delete(book_model)
            db.commit()
            return{"message":"Book deleted successfully"}
        else:
            raise HTTPException(status_code=403,detail='Action Is Forbidden')
    else:
        raise HTTPException(status_code=403,detail="Role not found")

# @router.get("/books/{book_id}",status_code=status.HTTP_200_OK)
# async def get_book_by_id(book_id:int=Path(gt=0)):
#     for book in Books:
#         if book.get('id') == book_id:
#             return book
#     raise HTTPException(status_code=404,detail="ID not found")

# current user will first check the authenticity of jwt token and then execute the endpoint if valid
@router.get("/books/{book_id}",status_code=status.HTTP_200_OK,response_model=Book_Response)
async def get_book_by_id(db:db_dependency,current_user:auth_dependency,book_id:int=Path(gt=0)):
    book_model = db.query(Books)
    # Admin can view all books but user can view only his book
    if current_user.get('role').casefold() == 'admin':
        book_model = book_model.filter(Books.id == book_id).first()
        if book_model is None:
            raise HTTPException(status_code=404,detail="ID not found")
        return book_model
    elif current_user.get('role').casefold() == 'user':
        book_model = book_model.filter(Books.owner_id == current_user.get('id'),Books.id == book_id).first()
        if book_model is None:
            raise HTTPException(status_code=404,detail="Requested book isnt available with that user.")
        return book_model
    else:
        raise HTTPException(status_code=403,detail="Role not found")


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
class Login_Request(BaseModel):
    username:str
    password:str


@router.post("/login")
async def create_jwt_token(db:db_dependency,creds:Login_Request):
    # find user in database
    user_model = db.query(Users).filter(Users.username == creds.username).first()
    if user_model is None:
        raise HTTPException(status_code=401,detail=f"User of {creds.username} not found")
    # get stored hashed
    stored_hashed = user_model.password
    if bcrypt_context.verify(creds.password,stored_hashed):
        # generate JWT
        token = create_access_token(creds.username,user_model.id,timedelta(minutes=20),user_model.role)
        return token
        
    else:
        raise HTTPException(status_code=401,detail='Invalid username or password')

   
