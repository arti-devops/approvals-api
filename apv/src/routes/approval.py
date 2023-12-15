#apv/src/routes/approval.py
from bson import ObjectId
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..services.mongodb import get_collection
from auth.src.services.encode_decode import decode_token

approval_router = APIRouter(prefix="/approval", tags=["Approvals management services"])

#TODO All Results should match to loggedin user

@approval_router.post("/submit")
async def create_approval(item: dict, collection=Depends(get_collection)):
    timestamp = datetime.strptime(item['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
    item['createdAt'] = timestamp
    result = collection.insert_one(dict(item))
    item_id = str(result.inserted_id)
    return {"_id": item_id, **item}

@approval_router.get("/requests")
async def get_approval_requests(collection=Depends(get_collection), user=Depends(decode_token)):
    user_email =  user["sub"]
    queryCurrentUserRequests = {
        "$or": [
            {"createdBy": user_email},
            {
                "approvals.userEmail": user_email,
                "approvals.status": {"$ne": "disapproved"}
            }
        ],
        "status": {"$eq": "pending"}
    }
    result = list(collection.find(queryCurrentUserRequests))
    for item in result:
        item['_id'] = str(item['_id'])
    return result

@approval_router.get("/history")
async def get_approval_requests(collection=Depends(get_collection), user=Depends(decode_token)):
    user_email =  user["sub"]
    queryCurrentUserHistory = {
        "$or": [
            {"createdBy": user_email},
            {"approvals.userEmail": user_email}
        ],
        "status": {"$ne": "pending"}
    }
    result = list(collection.find(queryCurrentUserHistory))
    for item in result:
        item['_id'] = str(item['_id'])
    return result

@approval_router.get("/{approval_id}")
async def get_approval_requests(approval_id: str, collection=Depends(get_collection)):
    item = collection.find_one({"_id": ObjectId(approval_id)})
    if item:
        item["_id"] = str(item["_id"])  # Convert ObjectId to string
        return item
    return JSONResponse(status_code=404, content="Cannot find approval with ID: {approval_id}")

# Update
@approval_router.put("/{approval_id}")
async def update_approval(approval_id: str, updated_approval: dict, collection=Depends(get_collection)):
    result = collection.update_one({"_id": ObjectId(approval_id)}, {"$set": updated_approval})
    if result.modified_count == 1:
        return {"status": "success", "message": "Approval updated"}
    return JSONResponse(status_code=404, content="Cannot find approval with ID: {approval_id}")