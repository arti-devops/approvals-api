#routes/upload.py
from fastapi import APIRouter, File, UploadFile, Request, HTTPException

from src.services.upload import create_upload_file, read_file

upload_router = APIRouter(prefix="/file", tags=["File upload and read services"])

@upload_router.post("/upload/")
async def upload_file(request: Request, file: UploadFile = File(...)):
    return await create_upload_file(request, file)

@upload_router.get("/read/{filename}")
async def read_uploaded_file(filename: str):
    return read_file(filename)