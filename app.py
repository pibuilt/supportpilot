from fastapi import FastAPI
import time

app = FastAPI()


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": time.time()
    }