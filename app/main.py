import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import connect_to_db, close_db_connection
from app.api.v1.endpoints import router as api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Iniciando aplicação")
    await connect_to_db()

    yield

    logging.info("Desligando aplicação")
    await close_db_connection()


app = FastAPI(
    title="Query Builder API",
    description="Uma API para analytics customizável e flexível.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router, prefix="/api")


@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": "Analytics API está no ar!"}
