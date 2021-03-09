import base64
import requests

HEADERS = {
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Origin': 'https://www.ikea.com',
    'Referer': 'https://www.ikea.com/'
}

def visual_search(image_url):
    url = 'https://visual-intelligence.ikea.net/visual-search/v2/public/search'
    headers = HEADERS
    headers |= {
        'Host': 'visual-intelligence.ikea.net',
        'x-client-id': 'AIzaSyBX8RsOkAzdfM1WW0ZiHVG8q7coOdowdXk'
    }
    image = requests.get(image_url, HEADERS).content
    data = {'base64': base64.b64encode(image).decode('utf-8'),
            'n_responses': 20,
            'includeIdentify': True
            }
    request = requests.post(url, headers=headers, json=data)
    matched_items = request.json()[0]['products']
    res = []
    for item in matched_items[:3]:
        item_type, item_no = item['globalId'].split(',')
        is_combination = item_type != 'art'
        res.append({
            'item_no': item_no,
            'is_combination': is_combination
        })
    return res