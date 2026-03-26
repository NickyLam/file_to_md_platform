from fastapi import FastAPI

from backend.app.api.uploads import router as uploads_router

app = FastAPI(title="File to Markdown Platform")
app.include_router(uploads_router)


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
