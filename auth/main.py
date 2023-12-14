from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.routes.auth import auth_router

app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Add API version prefix to the router
api_version = "v1"
api_prefix = f"/api/{api_version}"

# Add routers
app.include_router(auth_router, prefix=api_prefix)

# This handler CATCHES all exceptions occuring into the app
@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": {"details":exc.detail}},
    )