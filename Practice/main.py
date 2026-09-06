# to run the entire workflow from single file and handle database creation
from fastapi import FastAPI
from database import engine
import model
import books

app = FastAPI()

model.Base.metadata.create_all(bind=engine)

app.include_router(books.router)