import base64
import requests

def visual_search(image_url):
    """
    Search for item from IKEA in image using their API.
    """
    visual_search_endpoint = 'https://visual-intelligence.ikea.net/visual-search/v2/public/search'
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Origin': 'https://www.ikea.com',
        'Referer': 'https://www.ikea.com/',
        'Host': 'visual-intelligence.ikea.net',
        'x-client-id': 'AIzaSyBX8RsOkAzdfM1WW0ZiHVG8q7coOdowdXk'
    }
    image = requests.get(image_url, headers).content
    payload = {
        'base64': base64.b64encode(image).decode('utf-8'),
        'n_responses': 20,
        'includeIdentify': True
    }
    response = requests.post(visual_search_endpoint, headers=headers, json=payload)
    matched_items = response.json()[0]['products']
    res = []
    for item in matched_items[:3]:
        item_type, item_code = item['globalId'].split(',')
        is_combination = item_type != 'art'
        res.append({
            'item_code': item_code,
            'is_combination': is_combination
        })
    return res

# test_url = 'https://www.ikea.com/ru/ru/images/products/malm-komod-s-6-yashchikami-belyy__0484884_pe621348_s5.jpg?f=xxxl'
# print(visual_search(test_url))
