from openai import OpenAI
import os
import json
from typing import List, Tuple, Dict
from pathlib import Path
from app.models.quiz import QuizCreate
from app.models.option import OptionBase


# Cliente actualizado
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class QuizGenerator:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model

    def generate_quizzes(self, text: str, num_questions: int = 5, num_options: int = 4) -> List[QuizCreate]:
        prompt = self._build_prompt(text, num_questions, num_options)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        content = response.choices[0].message.content
        return self._parse_response(content)

    def _build_prompt(self, text: str, num_questions: int, num_options: int) -> str:
        return (
            f"Lee el siguiente texto y genera {num_questions} preguntas de opción múltiple en español. "
            f"Cada pregunta debe tener exactamente {num_options} opciones, una de ellas correcta. "
            f"Devuelve ÚNICAMENTE un JSON válido con este esquema, sin explicaciones:\n\n"
            "[\n"
            "  {\n"
            "    \"questionText\": \"...\",\n"
            "    \"context\": \"...\",\n"
            "    \"difficulty\": 3.0,\n"
            "    \"options\": [\n"
            "      {\"text\": \"...\", \"is_correct\": true},\n"
            "      {\"text\": \"...\", \"is_correct\": false},\n"
            "      ...\n"
            "    ]\n"
            "  },\n"
            "  ...\n"
            "]\n\n"
            f"TEXTO:\n{text}\n"
        )

    def _parse_response(self, content: str) -> List[QuizCreate]:
        try:
            # 💡 Limpieza: eliminar bloques tipo markdown ```json ... ```
            if content.strip().startswith("```json"):
                content = content.strip().removeprefix("```json").removesuffix("```").strip()
            elif content.strip().startswith("```"):
                content = content.strip().removeprefix("```").removesuffix("```").strip()

            # Intentar parsear como JSON puro
            raw = json.loads(content)

            quizzes = []
            for item in raw:
                options = [
                    OptionBase(text=opt["text"], is_correct=opt["is_correct"])
                    for opt in item["options"]
                ]
                quizzes.append(QuizCreate(
                    questionText=item["questionText"],
                    context=item["context"],
                    difficulty=float(item.get("difficulty", 3.0)),
                    options=options
                ))
            return quizzes

        except json.JSONDecodeError as e:
            print("❌ JSON inválido recibido del modelo:\n", content)
            raise ValueError("La respuesta del modelo no es válida JSON")

# Instancia global para reutilizar el modelo cargado
quiz_generator = QuizGenerator()