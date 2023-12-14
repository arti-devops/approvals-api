#auth/src/services/mongodb.py
from pymongo import MongoClient

from ..services.environnement import env

# MongoDB configuration from .env
MONGO_URI = env("MONGO_URI")
DATABASE_NAME = env("DATABASE_NAME")
COLLECTION_USERS = env("COLLECTION_USERS")

# MongoDB configuration
client = MongoClient(MONGO_URI)
database = client[DATABASE_NAME]
collection = database[COLLECTION_USERS]

# Dependency to get the MongoDB collection
def get_collection():
    return collection