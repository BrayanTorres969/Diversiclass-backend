from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from typing import Optional

class AuthService:
    
    @staticmethod
    def get_user_by_id(uid: str):
        """Obtiene un usuario de Firebase por su UID"""
        try:
            return auth.get_user(uid)
        except FirebaseError as e:
            raise ValueError(f"Error al obtener usuario: {str(e)}")
    
    @staticmethod
    def verify_token(id_token: str) -> dict:
        """Verifica un token JWT de Firebase"""
        try:
            return auth.verify_id_token(id_token)
        except FirebaseError as e:
            raise ValueError(f"Token inválido: {str(e)}")