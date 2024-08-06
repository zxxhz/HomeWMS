from fastapi import APIRouter
from utils import (
    authenticate_user,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    timedelta,
    Token,
    FormData,
    HTTPException,
    status,
    Depends,
    User
)

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: FormData):
    """这里定义了一个接口，路径为 /token, 用于用户申请tokens
    :param form_data:
    """
    # 首先对用户做出检查
    user = authenticate_user(form_data.username, form_data.passwd)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 定义tokens过期时间
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # 创建token
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # 返回token信息，JavaScript接收并存储，用于下次访问
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息
    :param current_user:
    :return:
    """
    return current_user
