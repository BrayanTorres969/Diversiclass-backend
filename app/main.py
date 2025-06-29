from fastapi import FastAPI
from app.api import courses, auth, documents,users # Importa tus rutas
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Plataforma de Cursos")

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # O ["*"] para desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(documents.router)

@app.get("/")
def home():
    return {"message": "¡Bienvenido a la API!"}