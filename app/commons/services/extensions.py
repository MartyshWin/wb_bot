import json
import random
import string
import logging

from app.schemas.general import ResponseModel


class BaseHandlerExtensions:
    def __init__(self):
        self.lang: dict = {}
