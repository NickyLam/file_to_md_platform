from fastapi import FastAPI

from backend.app.api.status import router as status_router
from backend.app.api.uploads import router as uploads_router

app = FastAPI(title="File to Markdown Platform")
app.include_router(uploads_router)
app.include_router(status_router)


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
