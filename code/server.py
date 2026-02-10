"""
Hardened backend server for Broken Arrow (v0.1).

Security features:
- API key authentication via `X-API-Key` header
- Restricted CORS (localhost only, GET only)
- Secure HTTP headers (HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy)
- No sensitive data in responses

Run (development only, HTTP):
    uvicorn server:app --reload --host 127.0.0.1 --port 8000

For production, you MUST:
- Put this behind a reverse proxy (e.g. nginx, Caddy) terminating HTTPS
- Store API key in an environment variable, not in code

Requires:
    pip install fastapi uvicorn
"""

import os
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


APP_NAME = "Broken Arrow"
APP_VERSION = "0.1"
APP_AUTHOR = "akameda"

# Load API key from environment; fall back to a default (strongly recommend overriding)
API_KEY = os.getenv("AKAMEDA_API_KEY", "change-this-api-key-now")


def verify_api_key(x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None) -> None:
    """
    Very simple API key check.
    All endpoints depend on this to ensure only trusted clients can call the API.
    """
    if x_api_key is None or x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


app = FastAPI(title=APP_NAME, version=APP_VERSION)

# Restrictive CORS: only allow localhost and GET requests, for simple browser calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["X-API-Key"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Add common security headers to all responses.
    """
    response = await call_next(request)
    response.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload")
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    return response


ApiKeyDep = Annotated[None, Depends(verify_api_key)]


@app.get("/")
def root(_: ApiKeyDep):
    """
    Basic health/info endpoint.
    Does not leak implementation details beyond name/version/author.
    """
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "author": APP_AUTHOR,
        "status": "ok",
    }


@app.get("/info")
def info(_: ApiKeyDep):
    """
    Detailed (but non-sensitive) server/browser info endpoint.
    """
    return JSONResponse(
        {
            "name": APP_NAME,
            "version": APP_VERSION,
            "author": APP_AUTHOR,
            "description": "Backend service for Akameda Browser providing basic API endpoints.",
        }
    )


@app.get("/ping")
def ping(_: ApiKeyDep):
    """
    Lightweight liveness check.
    """
    return {"pong": True}

