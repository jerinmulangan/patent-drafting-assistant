# extra_endpoints.py
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from typing import List
import os

from models.mongo_models import MongoDoc
from services import mongo_service, sql_service
from models.sql_models import ItemCreate, ItemResponse

router = APIRouter()

# --- File Upload ---
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class FileUploadResponse(BaseModel):
    filename: str
    size: int
    saved_path: str
    content_snippet: str

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    decoded_text = contents.decode("utf-8", errors="ignore")

    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        f.write(contents)

    return FileUploadResponse(
        filename=file.filename,
        size=len(contents),
        saved_path=save_path,
        content_snippet=decoded_text[:200]
    )

# --- MongoDB Routes ---
@router.post("/docs")
def create_mongo_doc(doc: MongoDoc):
    return mongo_service.create_doc(doc)

@router.get("/docs")
def read_mongo_docs():
    return mongo_service.get_docs()

# --- SQL Routes ---
@router.post("/items", response_model=ItemResponse)
def create_sql_item(item: ItemCreate):
    return sql_service.create_item(item)

@router.get("/items", response_model=List[ItemResponse])
def read_sql_items():
    return sql_service.get_items()
