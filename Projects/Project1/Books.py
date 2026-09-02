from fastapi import FastAPI
from fastapi import Body

app = FastAPI()

Books = [
    {'title':'Title One', 'author':'Author One', 'category':'Science'},
    {'title':'Title Two', 'author':'Author Two', 'category':'Science'},
    {'title':'Title Three', 'author':'Author Three', 'category':'History'},
    {'title':'Title Four', 'author':'Author Four', 'category':'Math'},
    {'title':'Title Five', 'author':'Author Five', 'category':'Math'},
    {'title':'Title Six', 'author':'Author Two', 'category':'Math'}
]

# Get books by category using Query Parameter
@app.get("/books/category/")
async def get_book_by_category(category:str):
    result = [book for book in Books if book.get('category').casefold() == category.casefold()]
    return result
        
# Get all books
@app.get("/books")
async def get_all_books():
    return{"message":"All books displayed","book":Books}

# Get all books by specific author using Query Parameter
@app.get("/books/byauthor/")
async def get_book_by_author(author:str):
    result = [book for book in Books if book.get('author').casefold() == author.casefold()]
    return {"message":f"Book by author{author}","Book":result}
        
# Create books using POST HTTP Method
@app.post("/books/createbook")
def create_new_book(new_book = Body()):
    Books.append(new_book)
    return {"message":"New Book Added","book":new_book}

# Update book using PUT HTTP Method
@app.put("/books/update_book")
def update_existing_book(updated_book=Body()):
    for index,book in enumerate(Books):
        if book.get('title').casefold() == updated_book.get('title').casefold():
            Books[index] = updated_book
            return {"message":"Book updated successfully","book":book.get('title')}
        
# Get book by title using Path Parameter
@app.get("/books/{title_of_book}")
async def get_book_by_title(title_of_book:str):
    book_returned = [book for book in Books if book.get('title').casefold() == title_of_book.casefold()]
    return{"message":f"Book matching title {title_of_book}","book":book_returned}

# Get book by title and category using dynamic parameter and query parameter
@app.get("/books/title/{title_of_book}/category/")
async def get_book_by_title_and_category(title_of_book:str,category:str):
    for book in Books:
        if book.get('title').casefold() == title_of_book.casefold() and book.get('category').casefold() == category.casefold():
            return{"message":f"Book with title {title_of_book} and category {category}","book":book}
        
# Delete books by title 
@app.delete("/books/delete_book/{book_title}")
async def delete_book_by_title(book_title):
    for book in Books:
        if book.get('title').casefold() == book_title.casefold():
            Books.remove(book)
            return{"message":"Book removed successfully","book":book}
