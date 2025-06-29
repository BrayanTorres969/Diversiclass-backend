from datetime import datetime
from typing import List,Optional
from app.models.course import CourseCreate
from app.models.course import CourseResponse
from app.services.firebase import db
from firebase_admin.exceptions import FirebaseError

class CourseService:
    
    @staticmethod
    async def create_course(course_data: CourseCreate,owner_id: str) -> CourseResponse:
        try:
             
            # 1. Preparamos los datos para Firestore
            course_dict = course_data.dict(exclude_unset=True, by_alias=True)

            firestore_data = {
                **course_dict,
                "ownerId": owner_id,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow()
            }
            
            #2. Creamos el documento
            doc_ref = db.collection("courses").document()
            doc_ref.set(firestore_data)
            
            # 3. Retornar respuesta
            return CourseResponse(
                **{
                    "id": doc_ref.id,
                    **firestore_data
                    
                }
            )
            
        except FirebaseError as e:
            raise ValueError(f"Error de Firestore: {str(e)}")
    
    @staticmethod
    def get_courses_by_user(user_id: str) -> List[CourseResponse]:
        try:
            docs = db.collection("courses").where("ownerId", "==", user_id).stream()

            return [CourseResponse(id=doc.id,  **doc.to_dict()) for doc in docs]
        
        except FirebaseError  as e:
            raise ValueError(f"Error al obtener cursos del usuario: {str(e)}")

    @staticmethod
    def get_course(course_id: str, requesting_user_id: Optional[str] = None) -> CourseResponse:
        try:
            
            doc = db.collection("courses").document(course_id).get()

            if not doc.exists:
                raise ValueError("Curso no encontrado")
                
            course_data = doc.to_dict()
            
            # Validación de ownership
            if requesting_user_id and course_data.get("ownerId") != requesting_user_id:
                raise ValueError("No tienes permisos para acceder a este curso")
            
            return CourseResponse(
                id=doc.id,
                **course_data
            )
            
        except FirebaseError as e:
            raise ValueError(f"Error al obtener curso: {str(e)}")