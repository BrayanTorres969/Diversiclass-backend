from datetime import datetime
from pathlib import Path 
from typing import List
from google.cloud import firestore
from app.services.firebase import db
from app.models import (
    DocumentCreate,
    DocumentResponse,
    QuizResponse,
    OptionResponse,
    QuizCreate,
    OptionBase
)


async def save_to_firestore(
    course_id: str,
    filename: str,
    file_path: str,
    quizzes: List[QuizCreate],
    title: str  # Añade este parámetro
) -> DocumentResponse:
    """Guarda documento y quizzes en Firestore con estructura relacional"""
    batch = db.batch()
    
    # 1. Crear referencia al documento principal
    doc_ref = db.collection("courses").document(course_id)\
               .collection("documents").document()
    document_id = doc_ref.id
    
    # 2. Datos del documento
    document_data = DocumentCreate(
        title=title,  # Añade el título
        originalName=filename,############### cambiar aca
        storagePath=file_path,
        fileType=Path(filename).suffix[1:],  # Extraer extensión sin el punto
        numQuestions=len(quizzes)
    ).dict(by_alias=True)
    
    document_data["processedAt"] = datetime.utcnow()
    
    # 3. Preparar quizzes y opciones para Firestore
    quizzes_data = []
    options_data = []
    
    for quiz_order, quiz in enumerate(quizzes, start=1):
        # Crear referencia para cada quiz
        quiz_ref = doc_ref.collection("quizzes").document()
        quiz_id = quiz_ref.id
        
        # Datos del quiz para Firestore
        quiz_data = {
            "questionText": quiz.question_text,
            "context": quiz.context,
            "difficulty": quiz.difficulty,
            "createdAt": datetime.utcnow(),
            "order": quiz_order
        }
        batch.set(quiz_ref, quiz_data)
        
        # Preparar opciones para este quiz
        for option_order, option in enumerate(quiz.options, start=1):
            option_ref = quiz_ref.collection("options").document()
            option_data = {
                **option.dict(),
                "order": option_order
            }
            batch.set(option_ref, option_data)
            
            # Guardar para la respuesta
            options_data.append({
                "quiz_id": quiz_id,
                "option_data": option_data,
                "option_id": option_ref.id
            })
        
        # Guardar para la respuesta
        quizzes_data.append({
            "quiz_id": quiz_id,
            "quiz_data": quiz_data
        })
    
    # 4. Añadir quizzes al documento principal (solo metadata)
    document_data["quizzes"] = [{
        "quizId": q["quiz_id"],
        "questionText": q["quiz_data"]["questionText"],
        "order": q["quiz_data"]["order"]
    } for q in quizzes_data]
    
    # 5. Añadir operación del documento principal
    batch.set(doc_ref, document_data)
    
    # 6. Actualizar contador en el curso padre
    course_ref = db.collection("courses").document(course_id)
    batch.update(course_ref, {
        "stats.documentCount": firestore.Increment(1),
        "stats.lastUpdate": datetime.utcnow()
    })
    
    # 7. Ejecutar todas las operaciones atómicamente
    batch.commit()
    
    document_data["createdAt"] = datetime.utcnow()
    document_data.pop("quizzes", None)  # Borra 'quizzes' si existe
    # 8. Construir respuesta estructurada
    return DocumentResponse(
        document_id=document_id,
        quizzes=[
            QuizResponse(
                quiz_id=q["quiz_id"],
                options=[
                    OptionResponse(
                        option_id=opt["option_id"],
                        **opt["option_data"]
                    ) for opt in options_data 
                    if opt["quiz_id"] == q["quiz_id"]
                ],
                **q["quiz_data"]
            ) for q in quizzes_data
        ],
        **document_data
    )

async def get_quizzes_by_document(course_id: str, document_id: str) -> List[QuizResponse]:
    try:
        quizzes_ref = db.collection("courses").document(course_id).collection("documents").document(document_id).collection("quizzes")
        docs = quizzes_ref.stream()

        quizzes = []


        for quiz_doc in quizzes_ref.stream():
            quiz_data = quiz_doc.to_dict()
            quiz_id = quiz_doc.id

            # Leer opciones de este quiz
            options_ref = quiz_doc.reference.collection("options")
            options = []

            for option_doc in options_ref.stream():
                option_data = option_doc.to_dict()
                option_data["optionId"] = option_doc.id
                options.append(OptionResponse(**option_data))

            # Agregar alias esperados
            quiz_data["quizId"] = quiz_id
            quiz_data["createdAt"] = quiz_data.get("createdAt", datetime.utcnow())
            quiz_data["options"] = options

            quizzes.append(QuizResponse(**quiz_data))
        
        return quizzes

    except Exception as e:
        raise ValueError(f"No se pudieron obtener los quizzes: {str(e)}")
