# Importation des classes de Pydantic dédiées à la gestion robuste des variables d'environnement
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Classe de configuration principale basée sur Pydantic v2.
    Elle charge, valide et type automatiquement les variables du fichier .env.
    """

    # Variables avec valeurs par défaut d'usine (Factory Defaults)
    APP_NAME: str = "Microservice IA"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # RECOMMANDATION DE SÉCURITÉ : Valeur de secours pour éviter un crash au démarrage
    MODEL_NAME: str = "kendrickfff/my_resnet50_garbage_classificationv1.2" 

    # Configuration interne du comportement de Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",              # Indique le nom du fichier contenant les variables d'environnement
        env_file_encoding="utf-8",    # Force l'encodage standard UTF-8 pour éviter les erreurs de lecture
        extra="ignore"                # Sécurité : Ignore les autres variables du .env non déclarées dans cette classe
    )


# ------------------------------------------------------------------------------
# INITIALISATION UNIQUE (SINGLETON PATTERN)
# ------------------------------------------------------------------------------
# On instancie la classe une seule fois. Pydantic parcourt immédiatement le .env,
settings = Settings()