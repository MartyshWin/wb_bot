from .extensions import BaseHandlerExtensions
from ..utils.language_loader import load_language
from app.schemas.general import ResponseModel
# from ...schemas.general import ResponseModel

class PaymentService(BaseHandlerExtensions):
    def __init__(self):
        super().__init__()
        self.link_pay: str | None = None

    def create_invoice(self) -> bool:
        self.link_pay = 'https://example.com'
        return True

    def get_invoice(self):
        pass

    @staticmethod
    def verification() -> bool:
        return True

    def error(self):
        pass

    def success_response(self, code_lang: str) -> ResponseModel:
        self.lang = load_language(code_lang)

        return self.format_response(
            text=self.lang['payment']
        )

    def canceled(self):
        pass

    def get_link_pay(self) -> str | None:
        return self.link_pay


