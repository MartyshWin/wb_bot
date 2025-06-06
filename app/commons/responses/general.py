from .extensions import BaseHandlerExtensions
from ..utils.language_loader import load_language
from app.schemas.general import ResponseModel
# from ...schemas.general import ResponseModel

class GeneralResponse(BaseHandlerExtensions):
    def __init__(self):
        # Если будет повторяться, то можно вынести в BaseHandlerExtensions
        super().__init__()
        self.lang = {}

    def start_command_response(self, user_id: int, user_name: str, code_lang: str, name: str) -> ResponseModel:
        self.lang = load_language(code_lang)

        return self.format_response(
            text=self.lang['start'].format(name=name),
            keyboard='start_kb'
        )

    def invite_command_response(self, code_lang: str) -> ResponseModel:
        self.lang = load_language(code_lang)

        return self.format_response(
            text=self.lang['invite'].format(link='https://t.me/private_fastnet_bot')
        )

    def help_command_response(self, code_lang: str) -> ResponseModel:
        self.lang = load_language(code_lang)

        return self.format_response(
            text=self.lang['help']
        )

    def lang_command_response(self, code_lang: str) -> ResponseModel:
        self.lang = load_language(code_lang)

        return self.format_response(
            text=self.lang['lang'],
            keyboard='lang_kb'
        )

    def privacy_command_response(self, code_lang: str) -> ResponseModel:
        self.lang = load_language(code_lang)

        return self.format_response(
            text=self.lang['privacy']
        )