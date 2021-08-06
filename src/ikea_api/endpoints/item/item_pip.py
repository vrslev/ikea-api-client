from __future__ import annotations

import asyncio
import re
from asyncio.tasks import Task
from typing import Any

import aiohttp

from ikea_api.constants import Constants
from ikea_api.errors import ItemFetchError

from . import build_headers, parse_item_code


def _async_fetch(urls: list[str | None], headers: dict[str, str]):
    async def main():
        async def fetch(session: aiohttp.ClientSession, url: str | None):
            if not url:
                return

            async with session.get(url=url, headers=headers) as response:
                try:
                    if response.status == 404:
                        raise ItemFetchError(response.url.__str__())
                    else:
                        return await response.json()
                except ItemFetchError as e:
                    url = e.args[0]
                    if not url:
                        return

                    opposite_url = build_opposite_url(url)
                    if not opposite_url:
                        return

                    r = await session.get(opposite_url, headers=headers)
                    if not r.ok:
                        raise ItemFetchError(parse_item_code(url))
                    return await r.json()

        async def fetch_all(session: aiohttp.ClientSession):
            tasks: list[Task[Any]] = []
            loop = asyncio.get_event_loop()
            for url in urls:
                task = loop.create_task(fetch(session, url))
                tasks.append(task)
            results = await asyncio.gather(*tasks)
            return results

        async with aiohttp.ClientSession() as session:
            res = await fetch_all(session)
            return res

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    res = loop.run_until_complete(main())
    return res


def build_url(item_code: str, is_combination: bool):
    if not len(item_code) == 8:
        return
    url = "{base_url}/{country}/{lang}/products/{folder}/{item_code}.json".format(
        base_url=Constants.BASE_URL,
        country=Constants.COUNTRY_CODE,
        lang=Constants.LANGUAGE_CODE,
        folder=item_code[5:],
        item_code="s" + item_code if is_combination else item_code,
    )
    return url


def build_opposite_url(url: str):
    match = re.findall(r"([sS])(\d{8})", url)
    if len(match) != 1:
        return
    match = match[0]
    len_ = len(match)
    is_combination = False
    if len_ == 1:
        item_code = match[0]
    elif len_ == 2:
        item_code = match[1]
        is_combination = True
    else:
        return
    return build_url(item_code, not is_combination)


def fetch(items: dict[str, bool]):
    # {'item_code': True (is SPR?)...}
    headers = build_headers({"Accept": "*/*"})
    headers.pop("Origin")
    urls: list[str | None] = [build_url(parse_item_code(i), items[i]) for i in items]
    responses = _async_fetch(urls, headers=headers)
    return [r for r in responses if r]
