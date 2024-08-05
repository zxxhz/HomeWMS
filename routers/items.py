from fastapi import APIRouter, HTTPException, Depends, Path
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient

router = APIRouter()


# Pydantic模型定义请求和响应的格式
class Item(BaseModel):
    name: str
    location: Optional[str] = None
    quantity: Optional[int] = None


# 假设这是我们的数据库
client: MongoClient = MongoClient(
    "**********"
)  # 替换为您的MongoDB连接字符串
db = client["HomeWMS"]  # 替换为您的数据库名称
collection = db["items"]  # 替换为您的集合名称



#获取物品信息 应该从数据库中搜索物品名字 返回物品位置和数量 用列表
@router.get("/items/{_id}", response_model=Item)
async def read_item(_id: str):
    item = collection.find_one({"_id": _id})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item(**item)


@router.post("/items", response_model=Item)
async def create_item(item: Item):
    item_id = collection.insert_one(item.model_dump()).inserted_id
    return Item(**item.model_dump(), _id=item_id)


@router.put("/items/{_id}", response_model=Item)
async def update_item(_id: str, item: Item):
    if collection.find_one({"_id": _id}) is None:
        raise HTTPException(status_code=404, detail="Item not found")
    collection.update_one({"_id": _id}, {"$set": item.model_dump()})
    return Item(**item.model_dump(), _id=_id)


@router.delete("/items/{_id}", response_model=Item)
async def delete_item(_id: str):
    if collection.find_one({"_id": _id}) is None:
        raise HTTPException(status_code=404, detail="Item not found")
    collection.delete_one({"_id": _id})
    return Item(**{"_id": _id})
