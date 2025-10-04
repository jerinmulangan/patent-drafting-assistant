from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from typing import Optional
from db import Base

# SQLAlchemy model
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)

# Pydantic models
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ItemResponse(ItemCreate):
    id: int
    class Config:
        orm_mode = True
