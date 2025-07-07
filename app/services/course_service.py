from datetime import datetime
from typing import List, Optional, Dict, Any
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
    """"
    @staticmethod
    def get_courses_by_user(user_id: str) -> List[dict]:
        try:
            docs = db.collection("courses").where("ownerId", "==", user_id).stream()

            return [{"id": doc.id, **doc.to_dict()} for doc in docs]
        
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
    """
    @staticmethod
    def get_courses_by_user(user_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los cursos de un usuario usando el mismo patrón que get_documents_by_course
        """
        try:
            # 1. Obtener documentos base
            courses_ref = db.collection("courses").where("ownerId", "==", user_id)
            docs = courses_ref.stream()
            
            # 2. Construir respuesta manualmente (igual que en get_documents_by_course)
            courses_list = []
            for doc in docs:
                course_data = doc.to_dict()
                courses_list.append({
                    "id": doc.id,  # Incluir ID explícitamente
                    "ownerId": course_data.get("ownerId"),
                    "createdAt": course_data.get("createdAt"),
                    "updatedAt": course_data.get("updatedAt"),
                    "title": course_data.get("title"),
                    "description": course_data.get("description"),
                    "isPublic": course_data.get("isPublic", False),
                    "tags": course_data.get("tags", []),
                    "documents": course_data.get("documents", [])
                })
            
            return courses_list
            
        except Exception as e:
            raise ValueError(f"Error al obtener cursos: {str(e)}")
        
    @staticmethod
    def get_documents_by_course(course_id: str) -> Dict[str, Any]:
        """
        Obtiene todos los documentos de un curso con la estructura específica requerida.
        Estructura Firestore:
            /courses/{courseId}
                └─ /documents  # Subcolección (antes llamada modules)
        """
        try:
            # 1. Obtener datos básicos del curso
            course_ref = db.collection("courses").document(course_id)
            course_doc = course_ref.get()
            
            if not course_doc.exists:
                raise ValueError("Curso no encontrado")

            course_data = course_doc.to_dict()
            
            # 2. Obtener DOCUMENTOS del curso (desde subcolección 'documents')
            documents = []
            docs_ref = course_ref.collection("documents").stream()  # Cambiado de 'modules' a 'documents'
            
            for doc in docs_ref:
                doc_data = doc.to_dict()
                documents.append({
                    "id": doc.id,
                    "title": doc_data.get("title", ""),
                    "description": doc_data.get("description", ""),
                    "duration": doc_data.get("duration", "0 horas"),
                    "progress": doc_data.get("progress", 0),
                    "completed": doc_data.get("completed", False),
                    "locked": doc_data.get("locked", False)
                })

            # 3. Calcular progreso global del curso
            total_docs = len(documents)
            if total_docs > 0:
                completed_docs = sum(1 for d in documents if d.get("completed"))
                progress = int((completed_docs / total_docs) * 100)
            else:
                progress = 0

            # 4. Construir respuesta (conservando el mismo formato JSON)
            return {
                "course": {
                    "id": course_id,
                    "title": course_data.get("title", "Sin título"),
                    "description": course_data.get("description", ""),
                    "duration": course_data.get("duration", "0 semanas"),
                    "difficulty": course_data.get("difficulty", "Principiante"),
                    "progress": progress,
                    "lastAccessed": course_data.get("lastAccessed", datetime.utcnow().isoformat()),
                    "modules": documents  # Key "modules" (frontend) -> contiene "documents" (backend)
                }
            }

        except Exception as e:
            raise ValueError(f"Error al obtener documentos: {str(e)}")