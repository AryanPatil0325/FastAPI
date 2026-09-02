from typing import Optional
from fastapi import FastAPI, HTTPException,Path,Query
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

# Book class
class Book:
    id:int
    title:str
    author:str
    description:str
    rating:int
    published_date:int

    def __init__(self,id,title,author,description,rating,published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

# Data validation class 
class BookRequest(BaseModel):
    id:Optional[int] = Field(description="ID value not required",default=None)
    title:str = Field(min_length=3)
    author:str = Field(min_lenght=1)
    description:str = Field(min_length = 3,max_length=100)
    rating:int = Field(gt=0,lt=6)
    published_date:int = Field(gt=1999,lt=2027)

    # Editing the Example Value shown in Swagger UI
    model_config = {
        "json_schema_extra":{
            "example":{
                "title":"A new book",
                "author":"Aryan Patil",
                "description":"Sample book description",
                "rating": 5,
                "published_date":2021
            }
        }
    }

# List of Book objects
Books = [
Book(1,'title 1','author 1','description 1',1,2021),
Book(2,'title 2','author 2','description 2',2,2022),
Book(3,'title 3','author 3','description 3',3,2023),
Book(4,'title 4','author 4','description 4',4,2024),
Book(5,'title 5','author 5','description 5',5,2022),
Book(6,'title 6','author 6','description 6',2,2021)
]

# Function to handle automatic ID assignment
def get_id_of_book(book:Book):
    if len(Books)>0:
        book.id = Books[-1].id+1
    else:
        book.id = 1
    return book

# API Endpoints

# Get all books
@app.get("/books",status_code=status.HTTP_200_OK) # adding explicit status code messages
async def get_all_books():
    return Books

# Create Book
@app.post("/books/create_book",status_code=status.HTTP_201_CREATED)
async def create_new_book(book_request:BookRequest):
    # originally the type of new book is BookRequest, so convert it to Book
    new_book = Book(**book_request.model_dump())
    Books.append(get_id_of_book(new_book))

# Get book by ID
@app.get("/books/{book_id}",status_code=status.HTTP_200_OK)
async def get_book_by_id(book_id:int = Path(gt=0)): # adding external validation to the Path parameters
    for book in Books:
        if book.id == book_id:
            return book
    # return{"message":"ID not found"} 
    # Raising a HTTP Exception if the book is not found
    raise HTTPException(status_code=404,detail="ID not found")

# Get books by Ratings
@app.get("/books/rating/",status_code=status.HTTP_200_OK)
async def get_books_by_rating(rating:int = Query(gt=0,lt=6)): # Adding external validation to the Query parameter
    books_list = [books for books in Books if books.rating == rating]
    return books_list

# Update Books with PUT 
@app.put("/books/update_book",status_code=status.HTTP_204_NO_CONTENT)
async def update_book(updated_book:BookRequest):
    # Boolean check for book found with id
    book_found = False
    for index,book in enumerate(Books):
        if book.id == updated_book.id:
            Books[index] = updated_book
            book_found = True
            return{"message":"Book updated","book":updated_book}
    # if book not found raise an exception
    if not book_found:
        raise HTTPException(status_code=404,detail="Book not found")

# Delete Books with Delete
@app.delete("/books/delete_book/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_by_title(book_id:int = Path(gt=0)): # adding external validation to the Path parameters
    book_found = False
    for book in Books:
        if book.id == book_id:
            Books.remove(book)
            book_found = True
            return{"message":"Book deleted","book":book}
    if not book_found:
        raise HTTPException(status_code=404,detail="Book not found")

# Get books by published date
@app.get("/books/published_date/{published_date}",status_code=status.HTTP_200_OK)
async def get_books_by_published_date(published_date:int = Path(gt=1999,lt=2034)): # adding external validation to the Path parameter
    result = [book for book in Books if book.published_date == published_date]
    return result