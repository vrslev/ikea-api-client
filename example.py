import json
from api import get_authorized_token, get_guest_token, Cart


def get_token(username=None, password=None):
    file_name = 'storage.json'
    try:
        open(file_name, 'x')
    except FileExistsError:
        pass
    with open(file_name, 'r+') as f:
        try:
            storage = json.load(f)
        except json.decoder.JSONDecodeError:
            storage = {'guest_token': '', 'authorized_token': ''}
        if username and password:
            if not storage['authorized_token']:
                storage['authorized_token'] = get_authorized_token(
                    username=username, password=password)
                f.seek(0)
                f.truncate()
                json.dump(storage, f)
            token = storage['authorized_token']
        else:
            if not storage['guest_token']:
                storage['guest_token'] = get_guest_token()
                f.seek(0)
                f.truncate()
                json.dump(storage, f)
            token = storage['guest_token']
    return token


token = get_token(username='username', password='password')
cart = Cart(token)
cart.add_items({'30457903': 1})
deliveries = cart.get_delivery_options('your_zip_code')
print(deliveries)
