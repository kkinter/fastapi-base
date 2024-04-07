from fastapi import FastAPI

from app.routes import auth, todos, users

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)


@app.get("/", status_code=200)
def read_root():
    return {"Hello": "World"}
