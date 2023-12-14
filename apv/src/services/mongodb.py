#apv/src/services/mongodb.py
from pymongo import MongoClient

from src.services.environnement import env

# MongoDB configuration from .env
MONGO_URI = env("MONGO_URI")
DATABASE_NAME = env("DATABASE_NAME")
COLLECTION_NAME = env("COLLECTION_NAME")

# MongoDB configuration
client = MongoClient(MONGO_URI)
database = client[DATABASE_NAME]
collection = database[COLLECTION_NAME]

# Dependency to get the MongoDB collection
def get_collection():
    return collection