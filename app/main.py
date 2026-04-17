import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.v1 import search, deals, redirect

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀  Starting {settings.app_name}")
    logger.info(f"    Mock data mode: {settings.use_mock_data}")

    # In production: await create_tables()
    yield

    logger.info("👋  Shutting down")
    from app.services.cache_service import close_redis
    await close_redis()


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description="Price comparison & affiliate redirect API for Amazon and Flipkart",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── Middleware ───────────────────────────────────────────────────────────────
app.add_middleware(GZipMiddleware, minimum_size=500)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production: ["https://yourapp.com"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# ─── Routes ──────────────────────────────────────────────────────────────────
app.include_router(search.router, prefix="/api/v1", tags=["Search"])
app.include_router(deals.router, prefix="/api/v1", tags=["Deals"])
app.include_router(redirect.router, prefix="/api/v1", tags=["Redirect"])


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "mock_mode": settings.use_mock_data,
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "health": "/health",
    }


# ─── Global error handler ─────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )
