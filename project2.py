from fastapi import FastAPI
from pydantic import BaseModel,Field
from typing import Optional

app = FastAPI()

# creating a Book class instead of directly updating the Books list
class Book:
    id:int
    title:str
    author:str
    description:str
    rating:int

    def __init__(self,id,title,author,description,rating):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating

# creating validation class using pydantic
class BookRequest(BaseModel):
    # id: Optional[int] = None
    # schema option in Swagger UI + same function as above
    id: Optional[int] = Field(description="ID is not needed while create",default=None)
    title:str = Field(min_length=3)
    author:str = Field(min_length=1)
    description:str = Field(min_length=1,max_length=100)
    rating:int = Field(gt=-1,lt=6) # 0-5 range

    # settings for Swagger UI using pydantic
    # setting the default example values to something valuable
    model_config = {
        "json_schema_extra":{
            "example":{
                "title":"title of book",
                "author": "author of book",
                "description":"some description of book",
                "rating": 5
            }
        }
    }



# Function to handle the ID parameter
def get_id(book:Book):
    book.id = 1 if len(Books) == 0 else Books[-1].id +1
    return book

# List of Book objects
Books = [
Book(1,'title 1','author 1','description 1',1),
Book(2,'title 2','author 2','description 2',2),
Book(3,'title 3','author 3','description 3',3),
Book(4,'title 4','author 4','description 4',4),
Book(5,'title 5','author 5','description 5',5),
Book(6,'title 6','author 6','description 6',2)
]

# Creating api endpoints

# 1. get all books
@app.get('/books')
async def get_all_books():
    return Books

# 2. Creating a add book endpoint
@app.post('/books/create_book')
async def create_book(book_request : BookRequest):
    # convert the book_request object to type Book
    new_book = Book(**book_request.model_dump())
    # append the new Book in Books
    Books.append(get_id(new_book))

# 3. Fetching Book by rating
@app.get('/books/{book_title}')
async def read_book_by_title(book_title:str):
    for book in Books:
        if book.get('title').casefold() == book_title.casefold():
            return book