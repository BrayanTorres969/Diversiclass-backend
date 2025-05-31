from pydantic import BaseModel, Field
from typing import Optional

class OptionBase(BaseModel):
    text: str
    is_correct: bool = Field(False, description="Si esta opción es la correcta")
    explanation: Optional[str] = Field(
        None,
        description="Explicación de por qué esta opción es correcta/incorrecta"
    )

class OptionCreate(OptionBase):
    pass

class OptionResponse(OptionBase):
    option_id: str = Field(..., alias="optionId")
    order: int = Field(..., description="Orden de visualización")

    class Config:
        allow_population_by_field_name = True