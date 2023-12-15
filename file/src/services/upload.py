#services/upload.py
import os
import json
import random
import string
import hashlib

from datetime import datetime

from fastapi import File
from fastapi import Request, UploadFile
from fastapi.responses import JSONResponse, FileResponse

from ..services.environnement import env

#TODO Retrive these values via env
UPLOAD_FOLDER = env("UPLOAD_FOLDER")
HASH_FILE_PATH = env("HASH_FILE_PATH")  # Path to the JSON file storing hashed filenames

def load_existing_hashes():
    # Load existing hashed filenames from the JSON file
    try:
        with open(HASH_FILE_PATH, "r") as hash_file:
            return set(json.load(hash_file))
    except FileNotFoundError:
        return set()

def save_hashes_to_file(hashes):
    # Save the hashed filenames to the JSON file
    with open(HASH_FILE_PATH, "w") as hash_file:
        json.dump(list(hashes), hash_file)

HASHED_FILES = load_existing_hashes()

def file_exists_by_hash(file_hash):
    return file_hash in HASHED_FILES

def generate_new_filename(original_filename):
    current_datetime = datetime.now()
    formatted_date = current_datetime.strftime("%m-%Y")
    
    # Extract the file extension from the original filename
    _, file_extension = os.path.splitext(original_filename)
    
    # Generate random characters for the new filename
    random_chars_g1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    random_chars_g2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    
    # Combine the random characters, formatted date, and file extension in the new filename
    new_filename = f"ARTI-{random_chars_g1}-{random_chars_g2}-{formatted_date}{file_extension}"
    
    return new_filename

def read_file(filename: str) -> str:
    # The file path
    file_path = os.path.join(env("UPLOAD_FOLDER"), filename)
    # Check if the file exists
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"detail": f"{filename} not found"})
    try:
        return FileResponse(file_path, filename=filename)
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

def read_avatar(username: str) -> str:
    # The file path
    file_path = os.path.join(env("AVATARS_FOLDER"), username)
    # Check if the file exists
    if not os.path.exists(file_path):
        return JSONResponse(status_code=404, content={"detail": f"{username} not found in {file_path}"})
    try:
        return FileResponse(file_path, filename=username, media_type="image/jpg")
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

# Function to be called by the router

async def create_upload_file(request: Request, file: UploadFile = File(...)):
    # Your existing logic for file upload goes here
    
    # Ensure that the upload folder exists or create it
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    try:
        # Read the entire file into memory
        file_content = await file.read()

        # Hash the content of the file using SHA-256
        hash_object = hashlib.sha256()
        hash_object.update(file_content)
        file_hash = hash_object.hexdigest()

        # Check if the file with the same hash already exists
        #TODO: Reenable hasj check
    #        if file_exists_by_hash(file_hash):
    #           return JSONResponse(content={"code":409,"message": "File with the same hash already exists", "hash": file_hash}, status_code=409)

        # Generate a new filename
        new_filename = generate_new_filename(file.filename)

        # Construct the full path to save the file
        file_path = os.path.join(UPLOAD_FOLDER, new_filename)

        # Save the file
        with open(file_path, "wb") as f:
            f.write(file_content)

        # Update the set of hashed files
        HASHED_FILES.add(file_hash)

        # Save the updated set of hashed filenames to the JSON file
        save_hashes_to_file(HASHED_FILES)

        # Generate a link to read the uploaded file
        file_link = str(request.url_for("read_uploaded_file", filename=new_filename))

        return JSONResponse(content={"code":200,"message": "File uploaded successfully", "filename": new_filename, "hash": file_hash, "link": file_link})
    except Exception as e:
        return JSONResponse(content={"code":500,"message": "Error uploading file", "error": str(e)}, status_code=500)