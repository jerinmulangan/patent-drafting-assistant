from pydantic import BaseModel, Field
from typing import Any

class MongoDoc(BaseModel):
    key: str
    value: Any

class MongoDocResponse(MongoDoc):
    id: str = Field(..., alias="_id")

# Helper for ObjectId -> str
def serialize_mongo_doc(doc):
    doc["_id"] = str(doc["_id"])
    return doc
