from datetime import datetime
from app.models.course import CourseCreate
from app.models.course import CourseResponse
from app.services.firebase import db

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
            firestore_data["_id"] = doc_ref.id
            doc_ref.set(firestore_data)
            
            # 3. Retornar respuesta
            return CourseResponse(
                **{
                    **firestore_data,
                    "id": doc_ref.id
                }
            )
            
        except Exception as e:
            raise ValueError(f"Error al crear curso: {str(e)}")

    @staticmethod
    def get_course(course_id: str) -> CourseResponse:
        try:
            doc_ref = db.collection("courses").document(course_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                raise ValueError("Curso no encontrado")
                
            data = doc.to_dict()
            return CourseResponse(
                id=doc.id,
                **data
            )
            
        except Exception as e:
            raise ValueError(f"Error al obtener curso: {str(e)}")