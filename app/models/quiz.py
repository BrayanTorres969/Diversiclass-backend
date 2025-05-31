from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
from .option import OptionBase, OptionResponse

class QuizBase(BaseModel):
    question_text: str = Field(..., alias="questionText")
    context: str = Field(
        ...,
        description="Fragmento del documento que originó esta pregunta"
    )
    difficulty: float = Field(
        1.0,
        ge=1.0,
        le=5.0,
        description="Dificultad estimada (1-5)"
    )

class QuizCreate(QuizBase):
    options: List[OptionBase]

class QuizResponse(QuizBase):
    quiz_id: str = Field(..., alias="quizId")
    created_at: datetime = Field(..., alias="createdAt")
    options: List[OptionResponse]

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }