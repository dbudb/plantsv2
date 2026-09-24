from fastapi import FastAPI
from pydantic import BaseModel
print("file loading")
app = FastAPI()

plants = []

class Plant(BaseModel):
    name: str
    species: str

@app.get("/")
def hello():
    print("hello called")
    return {"message": "hello plants"}
print("hello registered")

@app.get("/plants")
def plants():
    return plants

from db import db_engine
from models import Base

Base.metadata.create_all(db_engine)