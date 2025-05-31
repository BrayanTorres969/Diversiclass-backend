from fastapi import FastAPI
from app.api import courses, auth, documents,users # Importa tus rutas

app = FastAPI(title="Plataforma de Cursos")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(documents.router)

@app.get("/")
def home():
    return {"message": "¡Bienvenido a la API!"}