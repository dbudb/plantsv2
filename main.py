from fastapi import FastAPI

print("file loading")
app = FastAPI()

plants = []


@app.get("/")
def hello():
    print("hello called")
    return {"message": "hello plants"}


print("hello registered")


@app.get("/plants")
def plants():
    return plants
