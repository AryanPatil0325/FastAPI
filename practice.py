from fastapi import FastAPI

app = FastAPI()

# static api end point
@app.get('/greet')
async def greet():
    return {'message':'Hello All, Good Morning'}

# dynamic end point
@app.get('/books/{dynamic_param}')
async def get_dynamic(dynamic_param:str):
    return {'dynamic paramerter':dynamic_param}