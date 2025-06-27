import logging

from .extensions import BaseHandlerExtensions
from ..services.user import UserService
from ..utils.language_loader import load_language
from app.schemas.general import ResponseModel
# from ...schemas.general import ResponseModel

class GeneralResponse(BaseHandlerExtensions):
    def __init__(self):
        # Если будет повторяться, то можно вынести в BaseHandlerExtensions
        super().__init__()
        self.user_service = UserService()

    async def start_command_response(
            self,
            user_id: int,
            username: str,
            code_lang: str,
    ) -> ResponseModel:
        self.lang = load_language(code_lang)
        try:
            user = await self.user_service.get_or_create_user(user_id, username)

            return self.format_response(
                text=self.lang['start'],
                keyboard='start_kb'
            )
        except Exception as e:
            logging.error(f"Error in start_command_response: {e}", exc_info=True)
            return self.format_response(self.lang['error_occurred'])



    async def invite_command_response(self, code_lang: str) -> ResponseModel:
        self.lang = load_language(code_lang)

        return self.format_response(
            text=self.lang['invite'].format(link='https://t.me/private_fastnet_bot')
        )

    async def help_command_response(self, code_lang: str) -> ResponseModel:
        self.lang = load_language(code_lang)

        return self.format_response(
            text=self.lang['help']
        )

    async def lang_command_response(self, code_lang: str) -> ResponseModel:
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