from db import collection
from models.mongo_models import MongoDoc, serialize_mongo_doc

def create_doc(doc: MongoDoc):
    result = collection.insert_one(doc.model_dump())
    new_doc = collection.find_one({"_id": result.inserted_id})
    return serialize_mongo_doc(new_doc)

def get_docs():
    return [serialize_mongo_doc(doc) for doc in collection.find()]
