from fastapi import APIRouter, HTTPException
from firebase_admin import auth

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
async def login(token: str):
    try:
        decoded_token = auth.verify_id_token(token)
        return {"user_id": decoded_token["uid"]}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))