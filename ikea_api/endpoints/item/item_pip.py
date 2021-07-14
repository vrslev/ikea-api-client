import asyncio
import re
from typing import Dict

import aiohttp

from . import (
    Constants,
    ItemFetchError,
    build_headers,
    country_code,
    language_code,
    parse_item_code,
)


def _async_fetch(urls, headers):
    async def main():
        async def fetch(session, url):
            async with session.get(url=url, headers=headers) as response:
                try:
                    if response.status == 404:
                        raise ItemFetchError(response.url.__str__())
                    else:
                        return await response.json()
                except ItemFetchError as e:
                    url = e.args[0]
                    r = await session.get(build_opposite_url(url), headers=headers)
                    if not r.ok:
                        raise ItemFetchError(parse_item_code(url))
                    return await r.json()

        async def fetch_all(session):
            tasks = []
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


def build_url(item_code, is_combination):
    if not len(item_code) == 8:
        return
    url = "{base_url}/{country}/{lang}/products/{folder}/{item_code}.json".format(
        base_url=Constants.BASE_URL,
        country=country_code,
        lang=language_code,
        folder=item_code[5:],
        item_code="s" + item_code if is_combination else item_code,
    )
    return url


def build_opposite_url(url):
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
    return build_url(item_code, is_combination == False)


def fetch(items: Dict[str, bool]):
    # {'item_code': True (is SPR?)...}
    headers = build_headers({"Accept": "*/*"})
    headers.pop("Origin")
    urls = [build_url(parse_item_code(i), items[i]) for i in items]
    responses = _async_fetch(urls, headers=headers)
    res = []
    for r in responses:
        if r:
            res.append(r)
    return res
