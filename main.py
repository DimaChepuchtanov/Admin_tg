import uvicorn
from fastapi import FastAPI
from router.user import user
from router.post import router
from base.connect import engine
from base.model import Base


app = FastAPI()
app.include_router(user)
app.include_router(router)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    uvicorn.run('main:app')