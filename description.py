import re
from abc import ABC
from abc import abstractmethod
from typing import Type

import httpx

from entity import Property
from request import IChatGPTRequest

from entity import Description


class ITranslate(ABC):
    @abstractmethod
    def translate(self, en_text: str) -> Description:
        ...


class YandexTranslate(ITranslate):
    def __init__(self, api_key: str, folder_id: str):
        self.__api_key = api_key
        self.__folder_id = folder_id

    async def __translate(self, source_lang: str, target_lang: str, text: str):
        async with httpx.AsyncClient() as session:
            body = {
                "sourceLanguageCode": source_lang,
                "targetLanguageCode": target_lang,
                "texts": [
                    text
                ],
                "folderId": self.__folder_id}

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Api-Key {0}".format(self.__api_key)
            }
            response = await session.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                                          json=body,
                                          headers=headers
                                          )
            j = response.json()
            return j["translations"][0]["text"]

    async def translate(self, en_text: str) -> Description:
        ru = await self.__translate("en", "ru", en_text)
        ge = await self.__translate("en", "ka", en_text)
        return Description(ru=ru, ge=ge,en=en_text)


class ChatGPTTranslate(ITranslate):
    def __init__(self, request: Type[IChatGPTRequest]):
        self.__request = request

    @staticmethod
    def __generate_request_to_bot(en_text: str) -> (str, str):
        return f'translate this text in brackets "{en_text}" from english to russian and georgian, separate answer by semicolon'

    @staticmethod
    def __remove_under_symbol(s, symbol):
        t = ""
        if symbol in s:
            for item in s.split(";"):
                t += item.split(":")[1]
                t += ";"
            return t.strip()
        return s

    def translate(self, en_text: str) -> Description:
        response = self.__request.send(self.__generate_request_to_bot(
            en_text))  # English: I love cats and dogs; Georgian: მე ვეფხისტყაოს და ცხოვრებთან მოგაწვევით.
        if ":" in response:
            response = self.__remove_under_symbol(response, ":")
        split = response.split(";")
        ru_version = split[0]
        ge_version = split[1]
        return Description(ru=ru_version, en=en_text, ge=ge_version)


class IDescriptionGenerator(ABC):
    @abstractmethod
    async def generate(self, property: Property) -> Description:
        ...


class DescriptionGenerator(IDescriptionGenerator):
    def __init__(self, request: Type[IChatGPTRequest], translate: Type[ITranslate]):
        self.__request = request
        self.__translate = translate

    @staticmethod
    def __generate_request(property: Property) -> str:
        return f"write sales description to property object with {property.rooms.bedrooms} bedrooms and {property.rooms.living_room} living room, area is {property.area}m, located in good hood, good infrastructure in the hood,sunny side, address is {property.location.address}"

    async def generate(self, property: Property) -> Description:
        en_description = self.__request.send(self.__generate_request(property))
        en_description += f"\nPhone number: {property.agent.phone_number}, {property.agent.name}. Please, use this number. Phone number in account is incorrect."
        return self.__translate.translate(en_description)
