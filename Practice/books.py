# file that holds the endpoints
from typing import Optional,Annotated

from fastapi import APIRouter,HTTPException,Path,Query,Depends
from starlette import status
from pydantic import BaseModel,Field

from database import SessionFactory
from sqlalchemy.orm import Session

from model import Books

router = APIRouter()


def get_db():
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]

# Pydantic model for validations
class Book_Request(BaseModel):
    # id:Optional[int] = Field(description="ID field is not required",default=None)
    title:str = Field(min_length=3,max_length=100)
    author:str = Field(min_length=3)
    category:str = Field(min_length=3)
    price:int = Field(gt=0)
    owner_id:int = Field(gt=0)


# List of books
# Books = [
#     {
#         "id": 1,
#         "title": "Atomic Habits",
#         "author": "James Clear",
#         "category": "Self-Help",
#         "price": 499,
#         "owner_id": 1
#     },
#     {
#         "id": 2,
#         "title": "The Alchemist",
#         "author": "Paulo Coelho",
#         "category": "Fiction",
#         "price": 299,
#         "owner_id": 2
#     },
#     {
#         "id": 3,
#         "title": "Clean Code",
#         "author": "Robert C. Martin",
#         "category": "Programming",
#         "price": 799,
#         "owner_id": 1
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
#     {
#         "id": 6,
#         "title": "The Psychology of Money",
#         "author": "Morgan Housel",
#         "category": "Finance",
#         "price": 399,
#         "owner_id": 3
#     },
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

@router.get("/books",status_code=status.HTTP_200_OK)
async def get_all_books(
    db:db_dependency,
    author:Optional[str]=Query(None,min_length=3),
    category:Optional[str]=Query(None,min_length=3),
    limit:Optional[int]=Query(None,gt=0,lt=21)
    ):
    filtered_books = db.query(Books)
    
    if author is not None:
        # filtered_books = [book for book in filtered_books if book.get('author').casefold() == author.casefold()]
        filtered_books = db.query(Books).filter(Books.author.ilike(author.casefold()))
    
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
    

@router.post("/new_book",status_code=status.HTTP_201_CREATED)
async def create_new_book(db:db_dependency,new_book:Book_Request):
    book_model = Books(**new_book.model_dump())
    db.add(book_model)
    db.commit()
    return{"message":"Book created successfully"}

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

@router.put("/update_book/",status_code=status.HTTP_200_OK)
async def update_book(db:db_dependency,updated_book:Book_Request,id:int=Query(gt=0)):
    book_model = db.query(Books).filter(Books.id == id).first()
    if book_model is None:
        raise HTTPException(status_code=404,detail="ID not found")

    book_model.title = updated_book.title
    book_model.author = updated_book.author
    book_model.category = updated_book.category
    book_model.price = updated_book.price
    book_model.owner_id = updated_book.owner_id

    db.commit()


# @router.delete("/delete_book/{book_id}",status_code=status.HTTP_200_OK)
# async def delete_book(book_id:int=Path(gt=0)):
#     for index,book in enumerate(Books):
#         if book.get('id') == book_id:
#             Books.remove(book)
#             return {"message":"Book deleted successfully"}
#     raise HTTPException(status_code=404,detail="Book not found")

@router.delete("/delete_book/{book_id}",status_code=status.HTTP_200_OK)
async def delete_book(db:db_dependency,book_id:int=Path(gt=0)):
    book_model = db.query(Books).filter(Books.id == book_id).first()
    if book_model is None:
        raise HTTPException(status_code=404,detail="ID not found")
    db.delete(book_model)
    db.commit()
    return{"message":"Book deleted successfully"}

# @router.get("/books/{book_id}",status_code=status.HTTP_200_OK)
# async def get_book_by_id(book_id:int=Path(gt=0)):
#     for book in Books:
#         if book.get('id') == book_id:
#             return book
#     raise HTTPException(status_code=404,detail="ID not found")

@router.get("/books/{book_id}",status_code=status.HTTP_200_OK)
async def get_book_by_id(db:db_dependency,book_id:int=Path(gt=0)):
    book_model = db.query(Books).filter(Books.id == book_id).first()
    if book_model is None:
        raise HTTPException(status_code=404,detail="ID not found")
    return book_model

