from fastapi import APIRouter, File, UploadFile, HTTPException
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from app.operations.file_handling import folder_check
from app.operations.image_handling import convert_to_png, image_to_svg_conversion
from app.operations.mongo_db import fetch_mongodb_document, insert_mongodb_document
from app.database.mongo_db_data import client
from pathlib import Path
import os

load_dotenv(Path(os.getcwd()) / "app" / ".env")

img_to_svg = APIRouter(tags=["Image to SVG"])

db = client[os.getenv("DB_CLIENT_ID")]
collection = db[os.getenv("DB_NAME_IMAGE")]


@img_to_svg.get("/description")
def img_to_svg_des():
    return {"message": "In this functionality you have to provide a image of any type and I will return a svg file"}


@img_to_svg.post("/Upload_image")
async def img_to_svg_convert(file: UploadFile = File(...)):
    try:
        # Read the file into memory
        contents = await file.read()
        image = Image.open(BytesIO(contents))

        # Get basic information about the image
        width, height = image.size
        format_ = image.format

        check_folder = folder_check(type_="img_to_svg", image_type=format_)
        if not check_folder["status"]:
            raise HTTPException(status_code=500, detail="Could not able to create the files")

        conversion = convert_to_png(contents, file_name=file.filename)
        svg_data = await image_to_svg_conversion(image_path=conversion["image_path"],
                                                 image_name=conversion["image_name"])
        temp_doc = await fetch_mongodb_document(client_=os.getenv("DB_CLIENT_ID"), database=os.getenv("DB_NAME_IMAGE"),
                                                query={"docType": "Template", "description": "image to svg"})

        temp_doc["docType"] = "DATA"
        temp_doc["uploadedImage"] = str(conversion["uploaded_image_path"])
        temp_doc["updatedImage"] = str(conversion["image_path"])
        temp_doc["generatedImage"] = str(svg_data["SVG_path"])

        # mongoDB command
        await insert_mongodb_document(client_=os.getenv("DB_CLIENT_ID"), database=os.getenv("DB_NAME_IMAGE"),
                                      new_doc=temp_doc)

        return {
            **{
                "filename": file.filename,
                "format": format_,
            },
            **svg_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=e)
