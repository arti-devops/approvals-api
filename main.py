import random
import string
from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import hashlib
import json
from datetime import datetime
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

app = FastAPI()

# Allow requests from your Vue.js frontend
origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # You can adjust this based on your requirements
    allow_headers=["*"],  # You can adjust this based on your requirements
)

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "approvaldb"
COLLECTION_NAME = "approvals"

client = MongoClient(MONGO_URI)
database = client[DATABASE_NAME]
collection = database[COLLECTION_NAME]

# Dependency to get the MongoDB collection
def get_collection():
    return collection

UPLOAD_FOLDER = "uploads"
HASH_FILE_PATH = "file_hashes.json"  # Path to the JSON file storing hashed filenames

# Ensure that the upload folder exists or create it
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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

@app.get("/ping")
async def ping():
    return 'Good.'

@app.post("/uploadfile/")
async def create_upload_file(request: Request, file: UploadFile = File(...)):
    try:
        # Read the entire file into memory
        file_content = await file.read()

        # Hash the content of the file using SHA-256
        hash_object = hashlib.sha256()
        hash_object.update(file_content)
        file_hash = hash_object.hexdigest()

        # Check if the file with the same hash already exists
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

@app.get("/readfile/{filename}")
async def read_uploaded_file(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    return FileResponse(file_path, filename=filename)

@app.post("/approvals/submit")
async def create_item(item: dict, collection=Depends(get_collection)):
    timestamp = datetime.strptime(item['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
    item['createdAt'] = timestamp
    result = collection.insert_one(dict(item))
    item_id = str(result.inserted_id)
    return {"_id": item_id, **item}

#TODO Result should match to loggedin user
@app.get("/approvals/requests")
async def get_approval_requests(collection=Depends(get_collection)):
    result = list(collection.find({"status":"pending"}))
    for item in result:
        item['_id'] = str(item['_id'])
    return result

@app.get("/approvals/{approval_id}")
async def get_approval_requests(approval_id: str, collection=Depends(get_collection)):
    item = collection.find_one({"_id": ObjectId(approval_id)})
    if item:
        item["_id"] = str(item["_id"])  # Convert ObjectId to string
        return item
    raise HTTPException(status_code=404, detail="Item not found")
