from fastapi import FastAPI
from app.router.hello_world import router_hello
from app.router.img_to_svg import img_to_svg
from app.database.mongo_db_data import client
from app.schema.mongo_db import mongo_test_responcer
from app.router.dustbin_user import dustbin_user
from app.router.login import login_garbage

app = FastAPI()

# Include the routes from routes.py
app.include_router(router_hello)
app.include_router(img_to_svg)
app.include_router(dustbin_user)
app.include_router(login_garbage)

@app.get("/", tags=["Default api"])
def read_root():
    print("came here in the main file")
    return {"message": "Hello please open the docs page by http://127.0.0.1:8000/docs"}

@app.get("/mongo-test", tags=["MongoDB"], response_model=mongo_test_responcer)
def mongo_test():
    message = ''
    try:
        client.admin.command('ping')
        message = "Mongodb database connection is alive"
    except Exception as e:
        message = "Mongodb database connection is failed and triggered a error => " + e.message
    # Use the MongoDB database
    collections = client.list_database_names()  # Replace with your collection name
    print(collections)
    return {
        "message": message,
        "databases": collections}