import firebase_admin
from firebase_admin import credentials, storage, firestore
import os
from dotenv import load_dotenv
import json 

# Configuración para Render
if "RENDER" in os.environ:  # Verifica si está en producción
    firebase_config = json.loads(os.environ["FIREBASE_CREDENTIALS"])
    cred = credentials.Certificate(firebase_config)
    bucket_name = os.environ["FIREBASE_STORAGE_BUCKET"]
else:  # Desarrollo local
    from dotenv import load_dotenv
    load_dotenv()
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")

firebase_admin.initialize_app(cred, {
    "storageBucket": bucket_name
})


db = firestore.client()
bucket = storage.bucket()