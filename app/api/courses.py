from typing import List
from fastapi import APIRouter,Depends, HTTPException, status
from app.models.course import CourseCreate
from app.models.response import CourseResponse
from app.services.course_service import CourseService
from app.api.auth import get_current_user

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post(
    "/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_course(course_data: CourseCreate,owner_id: str = Depends(get_current_user)):
    try:
        return await CourseService.create_course(course_data, owner_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/user/me")
async def get_my_courses(user_id: str = Depends(get_current_user)):
    try:
        # Llama al servicio y devuelve directamente (sin parseo intermedio)
        return CourseService.get_courses_by_user(user_id)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: str,user_id: str = Depends(get_current_user)): 
    try:
        return CourseService.get_course(course_id,user_id)  # Quita await
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e))
    

@router.get("/{course_id}/documents")
async def get_documents_by_course(course_id: str):
    try:
        return CourseService.get_documents_by_course(course_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
