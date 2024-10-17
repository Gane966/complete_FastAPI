from fastapi import APIRouter

router_hello = APIRouter(tags=["Hello World"])

@router_hello.get("/hello")
def say_hello():
    return {"message": "Hello, World!"}
