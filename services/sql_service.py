from db import SessionLocal
from models.sql_models import Item, ItemCreate

def create_item(item: ItemCreate):
    db = SessionLocal()
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

def get_items():
    db = SessionLocal()
    items = db.query(Item).all()
    db.close()
    return items
