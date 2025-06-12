import json
import random
import string
import logging

from app.schemas.general import ResponseModel


class BaseHandlerExtensions:
    def __init__(self):
        self.lang: dict = {}
        self.box_types: dict[int, str] = {5: 'Монопаллеты', 6: 'Суперсейф', 2: 'Короба'}
        self.page_size: int = 10
