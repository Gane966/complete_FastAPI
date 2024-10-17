from app.database.mongo_db_data import client
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from datetime import datetime, timezone

current_time = datetime.now(timezone.utc)


async def fetch_mongodb_document(client_: str, database: str, query: dict, limit: int = 1):
    db = client[client_]
    collection = db[database]
    return await collection.find_one(query)


async def fetch_mongodb_documents(client_: str, database: str, query: dict, limit: int = 10):
    db = client[client_]
    collection = db[database]
    cursor = collection.find(query).limit(limit)
    return await cursor.to_list(length=limit)


async def insert_mongodb_document(client_: str, database: str, new_doc: dict):
    db = client[client_]
    collection = db[database]
    if "_id" in list(new_doc.keys()):
        new_doc.pop("_id")
    return await collection.insert_one(new_doc)


async def insert_mongodb_documents(client_: str, database: str, new_docs: list):
    db = client[client_]
    collection = db[database]
    for each in new_docs:
        if "_id" in list(each.keys()):
            each.pop("_id")
    return await collection.insert_many(new_docs)


async def update_mongodb_document(client_: str, database: str, query: dict, update_values: dict):
    db = client[client_]
    collection = db[database]
    update_values["updatedAt"] = current_time
    return await collection.update_one(query, {"$set": update_values})


async def update_mongodb_documents(client_: str, database: str, query: dict, update_values: dict):
    db = client[client_]
    collection = db[database]
    update_values["updatedAt"] = current_time
    return await collection.update_many(query, {"$set": update_values})


async def fetch_and_insert_document(client_: str, database: str, data: dict, template_Id: str) -> dict:
    """
    :param client_:
    :param database:
    :param data:
    :param template_Id: template I'd which you want to insert
    :return:
    """

    if template_Id:
        try:
            template_doc = await fetch_mongodb_document(client_, database, {"_id": ObjectId(template_Id)})
            template_doc["docType"] = "DATA"
            template_doc["message"] = data["message"]
            template_doc["name"] = data["name"]
            template_doc["imagePath"] = str(data["imagePath"])
            template_doc["location"] = {
                "state": data["state"],
                "local": data["local"],
                "country": "India",
                "district": data["district"],
                "pincode": ""
            }
            template_doc["updatedAt"] = current_time
            update_doc = await insert_mongodb_document(client_, database, new_doc=template_doc)

            return {"new_doc": update_doc, "status": True}
        except Exception as e:
            return {"message": f"Error fetching template: {e}", "status": False}

