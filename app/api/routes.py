from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ia_service import analyser_image  # Correction du nom de fichier
from app.shemas.prediction import AnalyseResponse

router = APIRouter(
    # prefix="/api/ia",
    # tags=["IA"]
)

# Limite stricte de taille : 10 Mo (10 * 1024 * 1024 octets)
MAX_FILE_SIZE = 10_485_760 

@router.post("/analyse", response_model=AnalyseResponse)
async def analyser(image: UploadFile = File(...)):

    if not image.content_type:
        raise HTTPException(
            status_code=400,
            detail="Type de fichier inconnu."
        )

    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être une image."
        )

    # Sécurité : Vérification de la taille du fichier avant la lecture complète
    if image.size and image.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="L'image est trop lourde. Limite maximale de 10 Mo."
        )

    image_bytes = await image.read()

    try:
        resultat = analyser_image(image_bytes)
        
        # Le dictionnaire renvoyé respecte parfaitement les champs requis par AnalyseResponse
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
