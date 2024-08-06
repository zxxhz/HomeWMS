from fastapi import APIRouter, HTTPException, Depends, status, Response
from pydantic import BaseModel
from typing import Optional
from routers.token import User, get_current_active_user
from database import find_one, insert_one, replace_one, delete_one
from bson.objectid import ObjectId


router = APIRouter()


# Pydantic模型定义请求和响应的格式
class Item(BaseModel):
    name: str
    location: Optional[str] = None
    quantity: Optional[int] = None


@router.get(
    "/items/{_id}",
    response_model=Item,
)
async def read_item(_id: str, current_user: User = Depends(get_current_active_user)):
    # 获取物品信息 应该从数据库中搜索物品id 返回物品位置和数量
    assert current_user
    item = find_one("items", {"_id": ObjectId(_id)})
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item(**item)


@router.post("/items", response_model=Item)
async def create_item(
    item: Item, current_user: User = Depends(get_current_active_user)
):
    # 增加物品
    assert current_user
    insert_one(dict(item))
    return item


@router.put("/items/{_id}", response_model=Item)
async def update_item(
    _id: str, item: Item, current_user: User = Depends(get_current_active_user)
):
    # 更新物品状态
    assert current_user
    result = replace_one(_id, dict(item))
    print(result)
    return item


@router.delete("/items/{_id}")
async def delete_item(
    _id: str, response: Response, current_user: User = Depends(get_current_active_user)
):
    # 删除物品
    assert current_user
    delete_one(_id)
    response.status_code = status.HTTP_204_NO_CONTENT
    return {}
