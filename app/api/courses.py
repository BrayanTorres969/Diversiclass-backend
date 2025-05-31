from fastapi import APIRouter, HTTPException, status
from app.models.course import CourseCreate
from app.models.response import CourseResponse
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post(
    "/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_course(course_data: CourseCreate):
    try:
        return CourseService.create_course(course_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: str): 
    try:
        return CourseService.get_course(course_id)  # Quita await
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e))
        