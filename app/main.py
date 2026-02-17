import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.tasks.processor import recovery_loop

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(recovery_loop())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


app = FastAPI(title="Webhook Processor", version="1.0.0", lifespan=lifespan)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def health():
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return {"status": "HEALTHY", "current_time": now}
