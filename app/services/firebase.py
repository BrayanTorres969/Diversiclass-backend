import firebase_admin
from firebase_admin import credentials, storage, firestore
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
firebase_admin.initialize_app(cred, {
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")
})


db = firestore.client()
bucket = storage.bucket()
