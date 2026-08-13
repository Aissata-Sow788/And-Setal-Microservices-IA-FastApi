from pydantic import BaseModel, HttpUrl


class AnalyseRequest(BaseModel):
    url_image: HttpUrl


class AnalyseResponse(BaseModel):
    type_incident: str
    score_confiance: float
    niveau_urgence: str