from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from pathlib import Path
from typing import List
from app.services.firebase import bucket
from app.services.document_service import save_to_firestore
from app.services.npl_service import quiz_generator 
from app.services.file_processor import extract_text_from_file 
from app.models.document import DocumentResponse
from app.models.quiz import QuizResponse


router = APIRouter(prefix="/courses/{course_id}/documents", tags=["Documents"])



@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir documento y generar preguntas",
    responses={
        200: {"description": "Documento procesado exitosamente"},
        400: {"description": "Formato de archivo no soportado"},
        422: {"description": "El documento no contiene suficiente texto"},
        500: {"description": "Error interno del servidor"}
    }
)
async def upload_document_and_generate_questions(
    course_id: str,
    file: UploadFile = File(..., description="Documento en formato PDF, DOCX o PPTX"),
    num_questions: int = Form(
        5, 
        gt=1, 
        le=20,
        description="Número de preguntas a generar (entre 1 y 20)"
    ),
    num_options: int = Form(
        4,
        gt=2,
        le=5, 
        description="Número de opciones por pregunta (entre 2 y 5)"
    )
):
    """
    Sube un documento y genera preguntas automáticas con estructura completa.
    
    Proceso:
    1. Valida el formato del archivo (PDF, DOCX, PPTX)
    2. Extrae el texto del documento
    3. Genera preguntas contextuales usando spaCy
    4. Almacena todo en Firestore con la estructura:
       - Documento principal
       - Quizzes (preguntas)
       - Options (opciones de respuesta)
    Devuelve el documento creado con todas sus preguntas y opciones.
    
    """
    try:
        # 1. Validar formato
        file_extension = Path(file.filename).suffix.lower()
        valid_extensions = ['.pdf', '.docx', '.pptx']

        #logger.info(f"Procesando archivo: {file.filename}")
        #logger.info(f"Tamaño del archivo: {file.size} bytes")
        
        if file_extension not in valid_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato {file_extension} no soportado. Use: {', '.join(valid_extensions)}"
            )
        
        # 2. Extraer texto
        try:
            text = await extract_text_from_file(file, file_extension) #es una función asíncrona (coroutine)
            if len(text.split()) < 30:  # Mínimo 30 palabras
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail="El documento no contiene suficiente texto")
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail= str(e)) 
        
        #logger.info(f"Texto extraído (primeros 100 chars): {text[:100]}") 
        # 3. Generar quizzes
        quizzes = quiz_generator.generate_quizzes(
            text=text,
            num_questions=num_questions,
            num_options=num_options
        )
        #logger.info(f"Número de quizzes generados: {len(quizzes)}")

        title = Path(file.filename).stem 
        
        # 4. Guardar en Firestore
        return await save_to_firestore(
            course_id=course_id,
            filename=file.filename,
            file_path=f"uploads/{file.filename}",
            quizzes= quizzes,
            title= title  # Añade este parámetro
        )
        
    except HTTPException as he:
        # Re-lanzar excepciones HTTP que ya fueron lanzadas
        raise he
    except ValueError as ve:
        # Para errores de validación de contenido
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(ve)
        )
    except Exception as e:
        # Para cualquier otro error inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al procesar documento: {str(e)}"
        )