from fastapi import FastAPI

from routers import items, token

app = FastAPI()


app.include_router(items.router)
app.include_router(token.router)
