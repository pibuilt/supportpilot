from fastapi.responses import JSONResponse


def success_response(data: dict, request_id: str):
    return JSONResponse(
        status_code=200,
        content={
            "data": data,
            "request_id": request_id
        }
    )


def error_response(message: str, request_id: str, status_code: int = 500):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": message,
                "request_id": request_id
            }
        }
    )