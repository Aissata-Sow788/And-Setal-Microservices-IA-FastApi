from io import BytesIO
from functools import lru_cache
from PIL import Image, UnidentifiedImageError
from transformers import pipeline
from app.core.config import settings

# Liste blanche des formats d'image autorisés pour l'application
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}

@lru_cache(maxsize=1)
def classer_image():
    """
    Initialise et met en cache le pipeline de classification d'images.
    Le décorateur @lru_cache évite de recharger le modèle lourd en mémoire 
    à chaque appel de la fonction analyser_image.
    """
    # Charge le nom du modèle depuis la configuration
    return pipeline(
        "image-classification",
        model=settings.MODEL_NAME
    )

def charger_image(image_bytes: bytes) -> Image.Image:
    """
    Valide les données binaires reçues, vérifie le format et retourne un objet PIL Image.
    """
    if not image_bytes:
        raise ValueError("Image vide.")

    try:
        # Utilisation de BytesIO pour simuler un fichier en mémoire à partir des octets
        with BytesIO(image_bytes) as stream:
            image = Image.open(stream)
            image.load()  # Force le chargement des pixels en mémoire pour valider l'image
            
            # Vérification stricte du format de l'image
            image_format = image.format
            if image_format not in ALLOWED_FORMATS:
                raise ValueError(f"Format non supporté : {image_format}")
            
            # Conversion systématique en RGB (supprime la transparence PNG / canal Alpha)
            return image.convert("RGB")

    # Interception des erreurs de formats invalides ou corrompus
    except UnidentifiedImageError:
        raise ValueError("Le fichier envoyé n'est pas une image valide.")
    except (OSError, SyntaxError):
        raise ValueError("L'image est corrompue ou illisible.")

# Cartographie liant les labels du modèle IA aux traductions et niveaux d'urgence applicatifs
CONFIGURATION_DECHETS = {
    # URGENCE ÉLEVÉE : Risques de pollution ou sanitaires immédiats
    "batteries": {"traduction": "Piles et Batteries", "urgence": "eleve"},
    "biological": {"traduction": "Déchets Biologiques", "urgence": "eleve"},
    
    # URGENCE MOYENNE : Recyclables standards ou déchets ménagers généraux
    "brown-glass": {"traduction": "Verre Marron", "urgence": "moyen"},
    "green-glass": {"traduction": "Verre Vert", "urgence": "moyen"},
    "white-glass": {"traduction": "Verre Transparent", "urgence": "moyen"},
    "metal": {"traduction": "Métal et Canettes", "urgence": "moyen"},
    "plastic": {"traduction": "Plastique", "urgence": "moyen"},
    "trash": {"traduction": "Déchets Divers", "urgence": "moyen"},
    
    # URGENCE FAIBLE : Déchets facilement recyclables ou peu dangereux
    "cardboard": {"traduction": "Carton", "urgence": "faible"},
    "paper": {"traduction": "Papier", "urgence": "faible"},
    "clothes": {"traduction": "Textiles et Vêtements", "urgence": "faible"},
    "shoes": {"traduction": "Chaussures", "urgence": "faible"}
}

def analyser_image(image_bytes: bytes) -> dict:
    """
    Fonction principale : charge l'image, execute l'IA et formate la réponse finale.
    """
    # Validation de l'image
    image = charger_image(image_bytes)
    
    # Récupération du modèle mis en cache
    classifier = classer_image()
    
    # Prédiction par le modèle Transformers
    predictions = classifier(image)
    if not predictions:
        raise ValueError("Le modèle IA n'a renvoyé aucune prédiction.")
        
    # Extraction du résultat le plus probable (le premier élément de la liste)
    meilleure_prediction = predictions[0] if isinstance(predictions, list) else predictions
    label_ia = meilleure_prediction["label"]
    score = round(meilleure_prediction["score"], 4) # Arrondi à 4 décimales

    # SÉCURITÉ : Si l'IA est incertaine (confiance < 50%), on applique une règle de repli
    if score < 0.50:
        return {
            "type_incident": "Déchets Divers (À vérifier)",
            "score_confiance": score,
            "niveau_urgence": "moyen"
        }

    # Si l'IA est sûre (>= 50%), récupération de la configuration correspondante
    info_dechet = CONFIGURATION_DECHETS.get(label_ia, {"traduction": label_ia, "urgence": "moyen"})

    return {
        "type_incident": info_dechet["traduction"],
        "score_confiance": score,
        "niveau_urgence": info_dechet["urgence"]
    }
