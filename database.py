from pymongo import MongoClient
from bson.objectid import ObjectId

client: MongoClient = MongoClient("mongodb://zxxhz:zxxhz@192.168.1.6:27017/")
# MongoDB连接URL
db = client["HomeWMS"]
# 数据库名称
collection_items = db["items"]
# 物品集合
collection_user = db["user"]


def find_one(collection: str, key: dict):
    if collection == "items":
        return collection_items.find_one(key)
    if collection == "user":
        return collection_user.find_one(key)


def insert_one(documents: dict):
    return collection_items.insert_one(documents)


def replace_one(document_id: str, documents: dict):
    return collection_items.replace_one({"_id": ObjectId(document_id)}, documents)


def delete_one(document_id: str):
    return collection_items.delete_one({"_id": ObjectId(document_id)})
