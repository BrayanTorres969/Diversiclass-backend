from datetime import datetime
from typing import List
from .base import TimestampMixin, OwnerMixin
from .course import CourseBase
from .document import DocumentResponse

class CourseResponse(CourseBase, TimestampMixin, OwnerMixin):
    """Respuesta completa de un curso con metadatos"""
    documents: List[DocumentResponse] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }