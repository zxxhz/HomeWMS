# 导入相关的模块
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


# 定义关于token的相关常量
# SECRET_KEY : 用于加密解密的密钥,只允许服务器知道,打死不告诉别人
#             可以执行 openssl rand -hex 32 获取一串随机的字符
# ALGORITHM  : 定义加密解密所使用的算法
# ACCESS_TOKEN_EXPIRE_MINUTES : token的有效期

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

class Token(BaseModel):
    """定义token的数据模型"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class FormData(BaseModel):
    username: str
    passwd: str


class User(BaseModel):
    """定义用户的数据模型"""

    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


# 创建一个加密解密上下文环境（甚至可以不用管这两句话啥意思）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """验证密码是否正确
    :param plain_password: 明文
    :param hashed_password: 明文hash值
    :return:
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """获取密码的hash值
    :param password: 欲获取hash的明文密码
    :return: 返回一个hash字符串
    """
    return pwd_context.hash(password)


def get_user(db, username: str):
    """查询用户
    :param db: 模拟的数据库
    :param username: 用户名
    :return: 返回一个用户的BaseModel(其实就是字典的BaseModel对象,二者可互相转换)
    """
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    """验证用户
    :param fake_db: 存储用户的数据库（这里是上面用字典模拟的）
    :param username: 用户名
    :param password: 密码
    :return:
    """
    # 从数据库获取用户信息
    user = get_user(fake_db, username)
    # 如果获取为空,返回None
    if not user:
        return None
    # 如果密码不正确,也是返回None
    if not verify_password(password, user.hashed_password):
        return None
    # 如果存在此用户,且密码也正确,则返回此用户信息
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建tokens函数
    :param data: 对用JWT的Payload字段,这里是tokens的载荷,在这里就是用户的信息
    :param expires_delta: 缺省参数,截止时间
    :return:
    """
    # 深拷贝data
    to_encode = data.copy()
    # 如果携带了截至时间,就单独设置tokens的过期时间
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # 否则的话,就默认用15分钟
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    # 编码,至此 JWT tokens诞生
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme), db=fake_users_db):
    # 获取当前用户信息,实际上是一个解密token的过程
    # :param token: 携带的token
    # :return:
    if db is None:
        db = {}
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解密tokens
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        # 如果没有获取到,抛出异常
        if payload.get("sub") is None:
            raise credentials_exception
        # 从tokens的载荷payload中获取用户名
        username: str = payload["sub"]
        token_data = TokenData(username=username)
    except JWTError as exc:
        raise credentials_exception from exc
    # 从数据库查询用户信息
    user = get_user(db, username=token_data.username)
    print(db)
    print(user)
    print(token_data)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """获取当前用户信息,实际上是作为依赖,注入其他路由以使用。
    :param current_user:
    :return:
    """
    # 如果用户被禁,抛出异常
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
