from io import BytesIO
from functools import lru_cache
from PIL import Image, UnidentifiedImageError
from transformers import pipeline
from app.core.config import settings

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

@lru_cache(maxsize=1)
def classer_image():
    # Charge 'yangy50/garbage-classification' défini dans votre .env
    return pipeline(
        "image-classification",
        model=settings.MODEL_NAME
    )

def charger_image(image_bytes: bytes) -> Image.Image:
    if not image_bytes:
        raise ValueError("Image vide.")

    try:
        with BytesIO(image_bytes) as stream:
            image = Image.open(stream)
            image.load()  
            
            image_format = image.format
            if image_format not in ALLOWED_FORMATS:
                raise ValueError(f"Format non supporté : {image_format}")
            
            return image.convert("RGB")

    except UnidentifiedImageError:
        raise ValueError("Le fichier envoyé n'est pas une image valide.")
    except (OSError, SyntaxError):
        raise ValueError("L'image est corrompue ou illisible.")

    
URGENCE_PAR_CATEGORIE = {
    "battery": "eleve",       # Piles/Batteries : Toxique, urgence élevée
    "biological": "eleve",    # Déchets biologiques : Risque sanitaire élevé
    "brown-glass": "moyen",   # Verre : Risque de coupure
    "green-glass": "moyen",
    "white-glass": "moyen",
    "metal": "moyen",         # Métal : Encombrant ou tranchant
    "plastic": "moyen",       # Plastique : Pollution visuelle et environnementale
    "cardboard": "faible",    # Carton : Moins dangereux, biodégradable plus vite
    "paper": "faible",        # Papier
    "trash": "moyen",         # Déchets divers
    "clothes": "faible"       # Textiles/Vêtements
}

def analyser_image(image_bytes: bytes) -> dict:
    image = charger_image(image_bytes)
    classifier = classer_image()
    
    predictions = classifier(image)
    if not predictions:
        raise ValueError("Le modèle IA n'a renvoyé aucune prédiction.")
        
    meilleure_prediction = predictions[0] if isinstance(predictions, list) else predictions
    label_ia = meilleure_prediction["label"]

    # 2. Récupération dynamique de l'urgence (renvoie "moyen" par défaut si le label est inconnu)
    urgence_calculee = URGENCE_PAR_CATEGORIE.get(label_ia, "moyen")

    return {
        "type_incident": label_ia,
        "score_confiance": round(meilleure_prediction["score"], 4),
        "niveau_urgence": urgence_calculee  # L'IA donne maintenant le vrai niveau
    }