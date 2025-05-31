from fastapi import APIRouter, HTTPException
from app.models.course import CourseCreate, CourseResponse
from app.services.course_service import CourseService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "/{user_id}/courses",
    response_model=CourseResponse,
    status_code=201,
    summary="Crear curso para un usuario (Pruebas)"
)
async def create_user_course_test(
    user_id: str,
    course_data: CourseCreate  # Datos del curso desde el body
):

    course_data.ownerId = user_id
    try:
        return await CourseService.create_course(
            course_data=course_data,
            owner_id=user_id  # Pasamos el ID desde la URL
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    
    except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={"type": "server_error", "message": "Error interno del servidor"}
            )