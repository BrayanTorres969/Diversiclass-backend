from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
from .quiz import QuizResponse

class DocumentBase(BaseModel):
    title: str
    file_type: str = Field(..., alias="fileType")
    original_name: str = Field(..., alias="originalName")
    storage_path: str = Field(..., alias="storagePath")

class DocumentCreate(DocumentBase):
    num_questions: int = Field(..., alias="numQuestions")

class DocumentResponse(DocumentBase):
    document_id: str= Field(..., alias="documentId")
    created_at: datetime = Field(..., alias="createdAt")
    processed_at: datetime = Field(..., alias="processedAt")
    quizzes: List[QuizResponse] = Field(default_factory=list)
    
    class Config:
        allow_population_by_field_name = True