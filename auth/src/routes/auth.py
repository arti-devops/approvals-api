from fastapi import APIRouter, Header, Depends

from ..services.mongodb import get_collection
from ..services.encode_decode import decode_token
from ..services.auth import process_login, process_logout

auth_router = APIRouter(prefix="/auth", tags=["Authentication services"])

@auth_router.post('/token')
async def login(authorization: str = Header(...), collection=Depends(get_collection)):
        return process_login(authorization, collection)

@auth_router.post('/logout')
async def logout(current_user = Depends(decode_token)):
    return process_logout(current_user)

@auth_router.get("/private-data")
async def get_private_data(current_user = Depends(decode_token)):
    return {"message": "You have access to this private data!", "user": current_user}
