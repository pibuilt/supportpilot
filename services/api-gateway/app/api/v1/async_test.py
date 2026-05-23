from fastapi import APIRouter

router = APIRouter()


@router.post("/test-async")
def test_async():
    return {
        "message": (
            "Use /v1/ingest for async testing"
        )
    }