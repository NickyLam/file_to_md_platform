from fastapi import FastAPI


app = FastAPI(title="File to Markdown Platform")


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
