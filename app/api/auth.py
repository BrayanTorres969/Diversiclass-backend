from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, exceptions
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    required: bool = True
) -> Optional[str]:
    """
    Valida el token JWT y retorna el UID.
    Si required=False y no hay token, retorna None en lugar de error.
    """
    try:
        if not credentials.scheme == "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Esquema de autenticación inválido"
            )
        decoded_token = auth.verify_id_token(credentials.credentials)
        return decoded_token["uid"]
    except (exceptions.InvalidIdTokenError, exceptions.ExpiredIdTokenError) as e:
        if not required:
            return None
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    except Exception as e:
        if not required:
            return None
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error de autenticación: {str(e)}"
        )

@router.get("/me")
async def get_user_data(user_id: str = Depends(get_current_user)):
    try:
        user = auth.get_user(user_id)
        return {
            "email": user.email,
            "uid": user.uid,
            "email_verified": user.email_verified
        }
    except exceptions.UserNotFoundError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")