import os
import json
import re
from abc import ABC
from abc import abstractmethod
from typing import List

import aiohttp
import httpx
import openai
import requests
from aiohttp import ClientSession


class IBrowserRequest(ABC):
    @abstractmethod
    async def send(self, script: str, proxy: str = None) -> str:
        ...


class BrowserRequest(IBrowserRequest):

    def __init__(self, browser_url: str, auth_password: str, machine_ip: str = None):
        self.__browser_url = browser_url
        self.__auth_password = auth_password
        self.__machine_ip = machine_ip

    async def send(self, script: str, proxy: str = None) -> str:
        p = {
            "options": {
                "timezoneId": "Asia/Tbilisi",
                "viewport": {
                    "width": 1920,
                    "height": 1080,
                    "deviceScaleFactor": 1
                },
                "geolocation": {
                    "latitude": 41.6941,
                    "longitude": 44.8337,
                    "accuracy": 45
                },
                "blockedResourceTypes": ["BlockCssAssets", "BlockImages", "BlockFonts", "BlockIcons", "BlockMedia"],
                "locale": "ru-GE"
            },
            "script": script
        }
        if proxy:
            p["options"]["upstreamProxyUrl"] = proxy
            if self.__machine_ip:
                p["options"]["upstreamProxyIpMask"] = {
                    "ipLookupService": "api.ipify.org",
                    "proxyIp": re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", proxy)[0],
                    "publicIp": self.__machine_ip
                }
        payload = json.dumps(p)
        headers = {
            'Authorization': self.__auth_password,
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(f"{self.__browser_url}/task", headers=headers, data=payload)
            if response.status_code > 220:
                raise Exception("wrong status code")
            return response.json()["output"]
        except Exception as e:
            print(e)
            async with ClientSession() as session:
                response = await session.post(f"{self.__browser_url}/task", headers=headers, data=payload, )
                j = await response.json()
                task_status = j["status"]
                if task_status == "FAILED" or task_status == "INIT_ERROR" or task_status == "TIMEOUT" or "BAD_ARGS":
                    raise
                return j["output"]


class IMyHomeRequest(ABC):
    @abstractmethod
    async def get_auth_page(self) -> str:
        ...

    @abstractmethod
    async def auth(self, login: str, password: str, form_token: str, proxy: str = None) -> str:
        ...

    @abstractmethod
    async def upload_images(self, images: List[str], ip: str, proxy: str = None):
        ...

    @abstractmethod
    async def add_product_stamp(self, auth_token: str, proxy: str = None) -> str:
        ...


class MyhomeRequest(IMyHomeRequest):
    def __init__(self, upload_images_app_url: str):
        self.__upload_images_app_url = upload_images_app_url

    async def get_auth_page(self) -> str:
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5,zh;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://auth.tnet.ge',
            'Referer': 'https://auth.tnet.ge/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        async with httpx.AsyncClient() as session:
            response = await session.get(
                "https://auth.tnet.ge/ru/user/login/?Continue=https://www.myhome.ge/", headers=headers)
            return response.text

    async def auth(self, login: str, password: str, form_token: str, proxy: str = None) -> str:
        url = "https://accounts.tnet.ge/api/ru/user/auth"
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5,zh;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://auth.tnet.ge',
            'Referer': 'https://auth.tnet.ge/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        data = {
            "Email": login,
            "Password": password,
            "CaptchaKey": "",
            "CaptchaSig": "",
            "FormToken": form_token,
            "Continue": "https://www.myhome.ge/ru/"
        }
        if proxy:
            if "http" in proxy:
                response = requests.post(url, headers=headers, proxies={"http": proxy})
                return response.json()["access_token"]
            elif "https" in proxy:
                response = requests.post(url, headers=headers, proxies={"https": proxy})
                return response.json()["access_token"]
            else:
                raise Exception("wrong proxy url")
        async with httpx.AsyncClient(timeout=4000) as session:
            response = await session.post(url, headers=headers, data=data)
            j = response.json()
        return j["data"]["access_token"]

    async def upload_images(self, images: List[str], ip: str, proxy: str = None):
        l = []
        async with httpx.AsyncClient() as session:
            for image in images:
                response = await session.post(f"{self.__upload_images_app_url}/upload",
                                              json={"filepath": os.path.abspath(image),
                                                    "ip": ip})
                l.append(response.json()["url"])
        print(l)
        return l

    async def add_product_stamp(self, auth_token: str, proxy: str = None) -> str:
        url = "https://api.myhome.ge/ru/Mypage/AddProductSaveStap"
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6,zh-CN;q=0.5,zh;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.myhome.ge',
            'Referer': 'https://www.myhome.ge/ru/my/addProduct',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'authtoken': auth_token,
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        data = {
            'adtype_id': '0',
            'product_type_id': '1',
            'estate_type_id': '0',
            'address': '',
            'street_address': '',
            'currency_id': '3',
            'price': '0',
            'price_type_id': '0',
            'area_size': '0',
            'area_size_type_id': '1',
            'floor': '0',
            'rooms': '0',
            'bedrooms': '0',
            'yard_size': '0',
            'yard_size_type_id': '1',
            'parking_id': '1',
            'canalization': '0',
            'water': '0',
            'road': '0',
            'photos_count': '0',
            'img': '',
            'is_gel': 'true',
            'name_json': '{"ka":"", "en": "", "ru": ""}',
            'seo_title_json': '{"ka":"", "en": "", "ru": ""}',
            'pathway_json': '{"ka":"", "en": "", "ru": ""}',
            'flat_floors[0][price]': '0',
            'electricity': '0',
            'client_phone': '568654121',
            'comment_geo': '',
            'comment_eng': '',
            'comment_ru': '',
            'cad_code': '',
            'draftId': '',
            'data[284]': '1',
            'data[413]': '12',
            'data[431]': '3',
            'data[1016]': '568654121',
        }
        if proxy:
            if "http" in proxy:
                response = requests.post(url, headers=headers, proxies={"http": proxy})
                return response.json()["access_token"]
            elif "https" in proxy:
                response = requests.post(url, headers=headers, proxies={"https": proxy})
                return response.json()["access_token"]
            else:
                raise Exception("wrong proxy url")
        async with httpx.AsyncClient(timeout=4000) as session:
            response = await session.post(url, headers=headers,
                                          data=data)
            j = response.json()
        return j["Data"]["draft_id"]


class IChatGPTRequest(ABC):
    @abstractmethod
    def send(self, text: str) -> str:
        ...


class ChatGPTRequest(IChatGPTRequest):
    def __init__(self, api_key: str):
        self.__api_key = api_key

    def send(self, text: str) -> str:
        openai.api_key = self.__api_key

        # Set up the model and prompt
        model_engine = "text-davinci-003"

        # Generate a response
        completion = openai.Completion.create(
            engine=model_engine,
            prompt=text,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )

        response = completion.choices[0].text
        print(response)
        return response
