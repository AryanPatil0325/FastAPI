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

# Query Parameter
@app.get('/books/')
async def read_book_by_query(category:str):
    result = [book for book in Books if book.get('category').casefold() == category.casefold()]
    return result
            


# Normal GET
@app.get('/books')
async def get_all_books():
    return Books


# List of books by specific author using query parameter
@app.get('/books/byauthor/')
async def read_books_by_author(author:str):
    book_by_author = [book for book in Books if book.get('author').casefold() == author.casefold()]
    return book_by_author

        
# POST HTTP request method to create books
@app.post('/books/create_book')
async def create_book(new_book = Body()):
    Books.append(new_book)
    return {'message':'New Book Added','Book':new_book}


# PUT HTTP request method to update books
@app.put('/books/update_book')
async def update_book(updated_book = Body()):
    for index,book in enumerate(Books):
        if book.get('title').casefold() == updated_book.get('title').casefold():
            Books[index] = updated_book
            return {'message':'Book updated successfully','book':updated_book} 

        
# Path Parameter
@app.get('/books/{book_title}')
async def get_book_by_title(book_title:str):
    for book in Books:
        if book.get('title').casefold() == book_title.casefold():
            return book


# List of books by title as dynamic parameter (Path parameter) and by category using query parameter
@app.get('/books/{book_title}/')
async def get_books_by_title_query(book_title:str,category:str):
    books_by_title_query = [book for book in Books if book.get('title').casefold() == book_title.casefold() and book.get('category').casefold() == category.casefold()]
    return books_by_title_query


# DELETE HTTP request method to delete books by title
@app.delete('/books/delete_book/{book_title}')
async def delete_book_by_title(book_title:str):
    for book in Books:
        if book.get('title').casefold() == book_title.casefold():
            Books.remove(book)
            return {'message':'Book removed successfully','removed_book':book_title}
