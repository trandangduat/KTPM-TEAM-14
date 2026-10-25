from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khoi tao bang trong co so du lieu neu chua ton tai
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API cho he thong dat hang Flash Sale",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Gan router v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"], summary="Kiem tra trang thai he thong")
def health_check(db: Session = Depends(get_db)):
    """Kiem tra tinh trang ket noi cua backend va co so du lieu."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
    }
