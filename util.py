import re
from typing import List
from aiohttp import ClientSession
import aiofiles


async def download_photos_and_get_all_paths(array_with_url: List[str]) -> List[str]:
    l = []
    async with ClientSession() as session:
        for url in array_with_url:
            async with aiofiles.open(f"{url}.jpeg", "rb") as file:
                response = await session.get(url)
                await file.write(await response.read())
            url += ".jpeg"
            l.append(url)
    return l


def get_ip_from_proxy(proxy: str) -> str:
    try:
        return re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", proxy)[0]
    except IndexError:
        return ""


