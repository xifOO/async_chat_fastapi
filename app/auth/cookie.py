from fastapi import Response

from app.config import settings


def set_refresh_cookie(response: Response, token: str) -> None:
    if response:
        response.set_cookie(
            key="refresh_token",
            value=token,
            httponly=True,
            secure=not settings.app.debug,
            samesite="lax",
            max_age=settings.auth.refresh_token_expires_minutes * 60,
            path="/auth/refresh",
        )


def delete_cookies(response: Response) -> None:
    if response:
        response.delete_cookie("refresh_token")
