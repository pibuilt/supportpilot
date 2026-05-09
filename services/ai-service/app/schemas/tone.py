from app.schemas.base import SupportPilotBaseModel


class ToneRequest(SupportPilotBaseModel):
    answer: str


class ToneResponse(SupportPilotBaseModel):
    final_response: str