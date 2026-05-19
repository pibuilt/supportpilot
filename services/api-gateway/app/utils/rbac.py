from fastapi import HTTPException


def require_admin(
    current_user: dict,
):
    if current_user["role"] not in [
        "admin",
        "root_admin",
    ]:
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return current_user


def require_root_admin(
    current_user: dict,
):
    if (
        current_user["role"]
        != "root_admin"
    ):
        raise HTTPException(
            status_code=403,
            detail="Root admin access required",
        )

    return current_user