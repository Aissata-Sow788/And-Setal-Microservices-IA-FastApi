from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.services.ia_service import classer_image  # Changé en ia_services (avec s)

# Préchauffage du modèle IA au démarrage
@asynccontextmanager
async def lifespan(app: FastAPI):
    classer_image()  # Charge le modèle en mémoire dès le démarrage
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Microservice IA pour l'analyse des signalements",
    lifespan=lifespan
)

# Configuration CORS pour le Frontend et Django
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion propre du routeur (le préfixe est géré directement ici)
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
