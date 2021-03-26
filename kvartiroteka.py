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


def download_images_from_selected_room(input_url):
    """
    Get all images from current page in IKEA's Russian Apartment Exhibition using their API.
    """
    session = requests.Session()
    design_id = re.search(r'#/[^/]+/[^/]+/([^/]+)', input_url)[1]
    design_room_url = 'https://kvartiroteka.ikea.ru/data/_/items/design_room' \
        + '?filter%5Bdesign_id.url%5D%5Beq%5D=' + design_id
    design_room = session.get(design_room_url, headers=HEADERS).json()
    image_urls = []
    for room in design_room['data']:
        room_url = 'https://kvartiroteka.ikea.ru/data/_/items/' \
            + 'block?fields=%2A.%2A%2Cviews.id%2Cviews.view_id.id%2Cviews.' \
            + 'view_id.navigation.%2A%2Cviews.view_id.image.%2A%2Cplanner_url_id.' \
            + '%2A.%2A&limit=-1&filter%5Broom_id%5D%5Beq%5D=' + str(room['room_id']) \
            + '&filter%5Bdesign_id%5D%5Beq%5D=' + str(room['design_id'])
        request = session.get(room_url, headers=HEADERS)
        for block in request.json()['data']:
            for view in block['views']:
                try:
                    image_url = view['view_id']['image']['data']['full_url']
                    # image_name = re.search(r'.*/(.*).jpg$', image_url)[1]
                    image_urls.append(image_url)
                    # print(re.search(r'.*/(.*).jpg$', image_url)[1])
                except TypeError:
                    pass
    return image_urls


def save_images(image_urls):
    for image_url in image_urls:
        file_name = 'photos/%s' % re.search(r'.*/(.*)$', image_url)[1]
        image = requests.get(image_url, stream=True)
        with open(file_name, 'wb') as file:
            file.write(image.content)


def download_and_save_images(input_url):
    image_urls = download_images_from_selected_room(input_url)
    save_images(image_urls)

# test_url = 'https://www.ikea.com/ru/ru/campaigns/kvartiroteka/#/p-3/three-room-83/tryohkomnatnaya-kvartira-dlya-semi/living-room/'
# download_and_save_images(test_url)
