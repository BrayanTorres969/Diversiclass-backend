from datetime import datetime
from pydantic import BaseModel, Field
from .base import TimestampMixin, OwnerMixin
from typing import List, Optional

class CourseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10)
    is_public: bool = Field(False, alias="isPublic")
    tags: List[str] = Field(default_factory=list)


class CourseCreate(CourseBase):
    """Versión temporal sin ownerId requerido"""
    ownerId: Optional[str] = None  # Campo opcional
    

class CourseResponse(CourseBase, TimestampMixin, OwnerMixin):
    """Modelo completo para respuesta, incluye timestamps y owner"""
    id: str = Field(..., alias="_id")
    _id: str = Field(None, exclude=True)  # Campo interno opcional

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str]
    is_public: Optional[bool]= None
    tags: Optional[List[str]] = None