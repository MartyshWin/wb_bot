from .extensions import BaseHandlerExtensions
from ..utils.language_loader import load_language
from app.schemas.general import ResponseModel


# from ...schemas.general import ResponseModel

class ProfileService(BaseHandlerExtensions):

    @staticmethod
    def create_profile() -> bool:
        return True

