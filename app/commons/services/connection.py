from .extensions import BaseHandlerExtensions
from ..utils.language_loader import load_language
from app.schemas.general import ResponseModel
# from ...schemas.general import ResponseModel
from .profile import ProfileService
from .payment import PaymentService

class ConnectionService(BaseHandlerExtensions):
    def __init__(self):
        super().__init__()
        self.profile: ProfileService = ProfileService()
        self.payment: PaymentService = PaymentService()

        self.db: dict = {
            '50gb': {
                'name': 'Пакет 50gb',
                'amount': 50,
                'price': 100,
            },
            '100gb': {
                'name': 'Пакет 100gb',
                'amount': 100,
                'price': 190,
            },
            '200gb': {
                'name': 'Пакет 200gb',
                'amount': 200,
                'price': 350,
            },
            '500gb': {
                'name': 'Пакет 500gb',
                'amount': 500,
                'price': 650,
            },
            '1000gb': {
                'name': 'Пакет 1000gb',
                'amount': 1000,
                'price': 1000,
            }
        }

    # Создать enums или pydantic модель для sender, где ожидается fast или full
    def information_alert_response(self, code_lang: str, sender: str) -> ResponseModel:
        self.lang: dict = load_language(code_lang)

        message = (
            self.lang['quick_connect']
            if sender == "fast"
            else self.lang['full_connect']
        )

        keyword = (
            'get_continue_kb(fast)'
            if sender == "fast"
            else 'get_continue_kb(full)'
        )

        return self.format_response(
            text=message,
            keyboard=keyword
        )

    def get_packages_list_response(self, code_lang: str) -> ResponseModel:
        self.lang: dict = load_language(code_lang)

        return self.format_response(
            text=self.lang['buy_package'],
            keyboard='package_selection_kb'
        )

    def package_selection_response(self, code_lang: str, package: str) -> ResponseModel:
        self.lang: dict = load_language(code_lang)
        rate = self.db[package]

        billing = self.create_billing()

        return self.format_response(
            text=self.lang['payment']['created'].format(rate=rate['name'], amount=rate['amount'], price=rate['price']),
            keyboard=f'create_billing({billing})'
        )

    def create_billing(self) -> str:
        """
        1. Создается счет (профиль)
        2. Создается ссылка на оплату и выдается пользователю
        3. Пользователь оплачивает
        4. Ему выдается инструкция и конфиг, взависимости от оплаченного (50ГБ, 100 ГБ, 200 ГБ, 500 ГБ, 1000 ГБ)

        :return: str
        """
        # 1. Создается счет (профиль)
        self.profile.create_profile()

        # 2. Создается ссылка на оплату и выдается пользователю
        self.payment.create_invoice()
        link: str = self.payment.get_link_pay()
        return link


    def connect_response(self, code_lang: str) -> ResponseModel:
        self.lang: dict = load_language(code_lang)

        check: bool = self.payment.verification()
        if check:
            return self.format_response(
                text=self.lang['payment']['success'].format(amount='1000'),
                keyboard='package_selection_kb'
            )
        else:
            return self.format_response(
                text=self.lang['payment']['error'],
            )