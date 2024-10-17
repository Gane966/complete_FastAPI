from fastapi import File, UploadFile, APIRouter, HTTPException, Query, Form
from app.operations.file_handling import folder_check
from fastapi.responses import JSONResponse
from app.operations.image_handling import convert_to_png
from datetime import datetime, timedelta, timezone
from PIL import Image
from io import BytesIO
from typing import List
from dotenv import load_dotenv
from pathlib import Path
from app.operations.mongo_db import (fetch_mongodb_document, insert_mongodb_document, update_mongodb_document,
                                     fetch_and_insert_document, fetch_mongodb_documents)
from app.operations.mail_fast_api import send_email
from passlib.context import CryptContext
from app.operations.api_handling import get_location_details_by_pincode
from app.schema.pincode_details import pincode_get_response
import os, jwt
from app.constnts import states, Districts, districts_data
from app.schema.pincode_details import UploadGarbageImage

load_dotenv(Path(os.getcwd()) / "app" / ".env")

# db = client[os.getenv("DB_CLIENT_ID")]
# collection = db[os.getenv("DB_NAME_IMAGE")]
dustbin_user = APIRouter(tags=["PINKY"])
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "7d9d58fb023c85aa87d93b68a2b44ddfc6d8f64aeb5c0aebed64fc71cb56a0d1"  # Change this to a strong secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@dustbin_user.get('/pincode/{pincode}', response_model=List[pincode_get_response])
async def get_pincode_details(pincode: str):
    details = await get_location_details_by_pincode(pincode)
    if details["status"] is True:
        state = details["data"][0].state
        district = details["data"][0].district
        pincode = details["data"][0].pincode
        # mongoBD update
        document = await fetch_mongodb_document(client_=os.getenv("DB_CLIENT_ID"), database=os.getenv("DB_NAME_IMAGE"),
                                                query={"docType": {"$ne": "Template"},
                                                       "location.state": state,
                                                       "location.district": district,
                                                       "location.pincode": pincode})
        if document is None:
            await insert_mongodb_document(client_=os.getenv("DB_CLIENT_ID"), database=os.getenv("DB_NAME_IMAGE"),
                                          new_doc={
                                              "docType": "DATA",
                                              "description": "Location",
                                              "locations": {
                                                  "country": details["data"][0].country,
                                                  "state": state,
                                                  "district": district,
                                                  "pincode": pincode,
                                                  "local": [area.location for area in details["data"]]
                                              }
                                          })
        else:
            await update_mongodb_document(client_=os.getenv("DB_CLIENT_ID"), database=os.getenv("DB_NAME_IMAGE"),
                                          query={"docType": "DATA",
                                                 "location.state": state,
                                                 "location.district": district,
                                                 "location.pincode": pincode},
                                          update_values={
                                              "locations": {"pincode": pincode,
                                                            "local": [area.location for area in details["data"]]}
                                          })

    elif details["status"] == "Invalid":
        raise HTTPException(status_code=500, detail="entered pincode is not valid")

    elif details["status"] == "Error":
        raise HTTPException(status_code=500, detail=details["status"].split("divide Error =>")[1])

    return details["data"]


@dustbin_user.post("/items/")
async def upload_file_with_dropdowns(
        file: UploadFile = File(...),  # File upload
        name: str = "",
        number: str = "",
        state: str = Query(..., description="Select  state", enum=states),
        district: str = Query(..., description="Select a secondary option", enum=Districts),
        area: str = ""):
    # Check if district exists in districts_data
    if district not in districts_data[state]:
        raise HTTPException(status_code=400, detail="Invalid district")
    print("U have upload ed the file")
    # Process the file and the selected options
    return {
        "filename": file.filename,
        "state": state,
        "district": district,
        "area": area
    }


@dustbin_user.post("/upload/", response_model=UploadGarbageImage)
async def upload_file(
        state: str,
        city: str,
        area: str,
        name: str,
        message: str,
        file: UploadFile = File(...),

):
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    format_ = image.format
    folder_check(type_="img_to_svg", image_type=format_)
    conversion = convert_to_png(contents, file_name=file.filename, type_="GARBAGE_IMAGE")
    try:
        # new_doc = await fetch_and_insert_document(client_=os.getenv("DB_CLIENT_ID"),
        #                                           database=os.getenv("DB_NAME_IMAGE"),
        #                                           data={"state": state, "local": area, "district": city,
        #                                                 "message": message,
        #                                                 "name": name,
        #                                                 "imagePath": conversion["uploaded_image_path"]},
        #                                           template_Id=os.getenv("USER_INPUT_FOR_GARBAGE_IMAGE_ID"))
        # if new_doc is None:
        #     raise HTTPException(status_code=500, detail=new_doc["message"])
        if send_email(
                to_address=os.getenv("MAIL_FROM"),  # Receiving email
                from_address=os.getenv("MAIL_FROM"),  # Sending email
                subject="Garbage Image Upload Confirmation",
                body=f"Dear {name},\n\nYour file has been uploaded successfully and Our team will take care of the "
                     f"garbage in short time.\n\nMessage: {message}\nCity: {city}\nArea: {area}\nState: {state}\n"
                     f"\nThank"
                     f"you :)"
        ):
            return {
                "message": "File uploaded successfully and email has been sent."
            }
        return {
            "message": "File uploaded successfully and mail has not been sent. Do not worry because the data has been "
                       "updated so our team will look into it."
        }
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


############### login ##############
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# Helper function to create access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@dustbin_user.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    # Find the user in the MongoDB collection
    try:
        user = await fetch_mongodb_document(client_=os.getenv("DB_CLIENT_ID"), database=os.getenv("DB_NAME_IMAGE"),
                                            query={"description": "Login", "username": username})
        print(user["area"])
        data = await fetch_mongodb_documents(client_=os.getenv("DB_CLIENT_ID"), database=os.getenv("DB_NAME_IMAGE"),
                                             query={"location.local": user["area"]})

        print(data)
        return_data = []
        for val in data:
            time = val["createdAt"].strftime("%Y-%m-%d %H:%M:%S")
            print(time)
            return_data.append({
                "Bin Number": val["_id"],
                "Request Time": time.split(" ")[1],
                "Request Date": time.split(" ")[0],
                "Status": val["status"],
                "Complaint": val["message"],
                "Location": val["location"]["local"]

            })

    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not user or not verify_password(password, user["password"]):
        # If user not found or password is incorrect
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # If login successful, create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer", "data": return_data}


@dustbin_user.post("/create_user/")
async def login(username: str = Form(...), password: str = Form(...), area: str = Form(...), ):
    hashed_password = pwd_context.hash(password)
    new_doc = {
        "username": username,
        "password": hashed_password,
        "area": area,
        "docType": "DATA",
        "description": "Login",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    try:
        user = await fetch_mongodb_document(client_=os.getenv("DB_CLIENT_ID"), database=os.getenv("DB_NAME_IMAGE"),
                                            query={"description": "Login", "username": username, "docType": "DATA"})
        if user is not None:
            raise HTTPException(status_code=400, detail="Username already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Some error occurred while entering the username value")
    await insert_mongodb_document(client_=os.getenv("DB_CLIENT_ID"), database=os.getenv("DB_NAME_IMAGE"),
                                  new_doc=new_doc)
    return {"message": "User created successfully"}
