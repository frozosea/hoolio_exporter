from abc import ABC
from abc import abstractmethod
from bs4 import BeautifulSoup
from entity import Property
from exception import *


class IMyHomeScrapper(ABC):
    @abstractmethod
    def get_form_token(self, string_html: str) -> str:
        ...


class MyHomeScrapper(IMyHomeScrapper):
    def get_form_token(self, string_html: str) -> str:
        soup = BeautifulSoup(string_html, "lxml")
        selector = soup.select_one("#FormToken")
        if not selector:
            raise MyHomeNotFormTokenException()
        value = selector.attrs["value"]
        if not value:
            raise MyHomeNotFormTokenException()
        return value


class MessageParser:
    @staticmethod
    def parse_message(message: str) -> Property:
        d = {item.split(":")[0].lower().strip(): item.split(":")[1].lower().strip() for item in message.split("\n")}
        if not ['тип операции', 'тип жилья', 'тип здания', 'дата сдачи дома', 'высота потолка', 'количество комнат',
                'количество спален', 'количество туалетов', 'количество залов', 'площадь квартиры', 'балкон',
                'отопление', 'горячая вода', 'источник', 'цена', 'газифицирован'
                ] in d.keys():
            raise TelegramTransportInvalidMessageFormat()
