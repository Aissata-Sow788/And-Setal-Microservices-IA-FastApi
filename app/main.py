# Importation du gestionnaire de contexte asynchrone pour piloter le cycle de vie de l'app
from contextlib import asynccontextmanager
from fastapi import FastAPI
# Importation du middleware de gestion des politiques de sécurité CORS
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings
from app.services.ia_service import classer_image  


# GESTION DU LIFESPAN (CYCLE DE VIE DE L'APPLICATION)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère les actions à exécuter au démarrage et à la fermeture du serveur.
    Crucial pour éviter le phénomène de 'Cold Start' (lenteur au premier appel).
    """
    # Action au démarrage : On télécharge/charge le modèle IA en mémoire (RAM/GPU)
    # Ainsi, lorsque le premier utilisateur soumettra une image, l'analyse sera instantanée.
    classer_image()  
    
    yield  # Sépare la phase de démarrage (au-dessus) de la phase de fermeture (en-dessous)
    
    # Action à la fermeture (optionnel) : Nettoyage ou libération des ressources ici.



# INITIALISATION DE L'APPLICATION FASTAPI

app = FastAPI(
    title=settings.APP_NAME,          # Titre dynamique récupéré depuis le fichier .env
    version=settings.APP_VERSION,      # Version dynamique récupérée depuis le fichier .env
    description="Microservice IA pour l'analyse des signalements",
    lifespan=lifespan                  # Injection du gestionnaire de cycle de vie créé ci-dessus
)



# CONFIGURATION DES MIDDLEWARES (SÉCURITÉ CORS)

# Le CORS (Cross-Origin Resource Sharing) empêche les piratages par injection de scripts.
# Ici, on le configure pour permettre les échanges fluides entre vos différents serveurs.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Autorise toutes les origines (indispensable pour l'appel de Django en local)
    allow_credentials=True,   # Autorise le partage des cookies et des en-têtes d'authentification
    allow_methods=["*"],      # Autorise toutes les méthodes HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],      # Autorise tous les en-têtes HTTP personnalisés
)


# ENREGISTREMENT ET ROUTAGE DES API VUES

# On greffe le routeur de l'application sur l'instance principale de FastAPI
app.include_router(
    router,
    prefix="/api/ia",         # Ajoute automatiquement le préfixe à toutes les routes du fichier routes.py
    tags=["IA"]               # Regroupe visuellement ces routes sous l'onglet 'IA' dans Swagger
)



# ROUTES DE CONTRÔLE DE BASE (HEALTH CHECKS)
@app.get("/")
def root():
    """Route racine pour vérifier rapidement via un navigateur si le serveur répond."""
    return {"message": "Microservice IA opérationnel"}


@app.get("/health")
def health():
    """
    Route de santé publique. Utilisée par les outils de déploiement (Docker, Kubernetes)
    pour monitorer l'état du microservice à intervalles réguliers.
    """
    return {"status": "ok"}
