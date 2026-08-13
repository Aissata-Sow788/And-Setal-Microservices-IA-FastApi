from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.services.ia_service import classer_image

# Préchauffage du modèle IA au démarrage (évite le lag au premier appel)
@asynccontextmanager
async def lifespan(app: FastAPI):
    classer_image()  # Charge le modèle en mémoire RAM/GPU dès le démarrage
    yield
    # Nettoyage si nécessaire à la fermeture

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Microservice IA pour l'analyse des signalements",
    lifespan=lifespan  # Ajout du cycle de vie
)

# Configuration CORS essentielle pour le Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production (ex: ["https://monfront.com"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    router,
    prefix="/api/ia",
    tags=["IA"]
)

@app.get("/")
def root():
    return {"message": "Microservice IA opérationnel"}

@app.get("/health")
def health():
    return {"status": "ok"}

from fastapi import UploadFile, File

@app.post("/api/ia/analyse", tags=["IA Force"])
async def analyser_ia_force(image: UploadFile = File(...)):
    return {"message": "Route forcee en direct depuis main.py"}

