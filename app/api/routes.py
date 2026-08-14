from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ia_service import analyser_image
from app.shemas.prediction import AnalyseResponse

# Initialisation du routeur isolé.
router = APIRouter()

# SÉCURITÉ MÉMOIRE : Limite stricte de la taille du téléversement fixée à 10 Mo (en octets)
# Empêche les attaques par déni de service (DoS) visant à saturer la RAM de votre serveur.
MAX_FILE_SIZE = 10_485_760  


# ------------------------------------------------------------------------------
# POINT D'ACCÈS (ENDPOINT) : ANALYSE DES SIGNALEMENTS
# ------------------------------------------------------------------------------

@router.post("/analyse", response_model=AnalyseResponse)
async def analyser(image: UploadFile = File(...)):
    """
    Réceptionne l'image binaire envoyée par Django, valide ses métadonnées,
    la transmet au pipeline Transformers et renvoie le verdict de classification.
    """

    # VALIDATION DU TYPE : Vérification de la présence et de la validité du type MIME
    # Filtre immédiatement les fichiers texte, PDF, archives zip, etc.
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être une image valide."
        )

    # VALIDATION DE LA TAILLE : Lecture des métadonnées du flux de fichiers sans chargement en mémoire
    if image.size and image.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="L'image est trop lourde. Limite maximale de 10 Mo."
        )

    # LECTURE DES DONNÉES BINAIRES
    image_bytes = await image.read()

    # EXÉCUTION DU LOGICIEL ET GESTION DES ERREURS
    try:
        # Transmission des octets de l'image brute au service de traitement de l'IA
        resultat = analyser_image(image_bytes)
        
        # Envoi de la réponse. FastAPI va automatiquement mapper ce dictionnaire sur AnalyseResponse.
        return resultat

    except ValueError as e:
        # Erreurs fonctionnelles (image vide, format de fichier rejeté par Pillow, image corrompue)
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
        
    except Exception as e:
        # Erreurs système ou d'infrastructure (panne Hugging Face, crash du pipeline d'analyse)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur du service IA : {str(e)}"
        )