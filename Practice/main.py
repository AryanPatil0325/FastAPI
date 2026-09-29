# to run the entire workflow from single file and handle database creation
from fastapi import FastAPI
from database import engine
import model
from router import books,auth

app = FastAPI()

model.Base.metadata.create_all(bind=engine)

app.include_router(books.router)
app.include_router(auth.router)