import re
import requests

HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json;charset=utf-8',
    'Origin': 'https://www.ikea.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'kvartiroteka.ikea.ru',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Referer': 'https://www.ikea.com/',
    'Accept-Language': 'ru',
    'Connection': 'keep-alive'
}

def parse_input_url(input_url):
    design_id = re.search(r'#/[^/]+/[^/]+/([^/]+)', input_url)[1]
    design_room_url = 'https://kvartiroteka.ikea.ru/data/_/items/design_room' \
            + '?filter%5Bdesign_id.url%5D%5Beq%5D=' + design_id
    return design_room_url

def fetch_design_room(url):
    return requests.get(url, headers=HEADERS).json()

def parse_design_room(design_room):
    room_urls = []
    for room in design_room['data']:
        room_urls.append('https://kvartiroteka.ikea.ru/data/_/items/' \
        + 'block?fields=%2A.%2A%2Cviews.id%2Cviews.view_id.id%2Cviews.' \
        + 'view_id.navigation.%2A%2Cviews.view_id.image.%2A%2Cplanner_url_id.' \
        + '%2A.%2A&limit=-1&filter%5Broom_id%5D%5Beq%5D=' + str(room['room_id']) \
        + '&filter%5Bdesign_id%5D%5Beq%5D=' + str(room['design_id']))
    return room_urls

def fetch_images(room_urls):
    images = []
    for room_url in room_urls:
        request = requests.get(room_url, headers=HEADERS)
        for block in request.json()['data']:
            for view in block['views']:
                images.append(view['view_id']['image']['data']['full_url'])
    return images

def get_images(input_url):
    design_room_url = parse_input_url(input_url)
    design_room = fetch_design_room(design_room_url)
    room_urls = parse_design_room(design_room)
    return fetch_images(room_urls)

# test_url = 'https://www.ikea.com/ru/ru/campaigns/kvartiroteka/#/464d/four-room-75/strogaya-planirovka-s-preobladaniem-tyomnyh-tonov/bedroom/'
# images = get_images(test_url)
