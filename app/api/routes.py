from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ia_service import analyser_image
from app.shemas.prediction import AnalyseResponse

# On crée le routeur sans préfixe pour éviter les doublons (ex: /api/ia/api/ia/analyse)
router = APIRouter()

MAX_FILE_SIZE = 10_485_760  # 10 Mo

@router.post("/analyse", response_model=AnalyseResponse)
async def analyser(image: UploadFile = File(...)):

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être une image valide."
        )

    if image.size and image.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="L'image est trop lourde. Limite maximale de 10 Mo."
        )

    image_bytes = await image.read()

    try:
        # Appel du vrai service IA avec le dictionnaire d'urgence dynamique
        resultat = analyser_image(image_bytes)
        return resultat

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur du service IA : {str(e)}"
        )
