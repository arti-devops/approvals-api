from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes.upload import upload_router

app = FastAPI()

# CORS Middleware
origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include services
app.include_router(upload_router)
#app.include_router(approval_service.router)
