import re
import json
import os
from ikea_api import (
    get_guest_token, Cart,
    OrderCapture, Auth, Profile)

token = ''
auth_token = ''


def save_json(r, *args, **kwargs):
    directory = 'response_examples'
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass
    module = re.findall(r'.([^.]+$)', r.__module__)[0]
    try:
        os.mkdir(os.path.join(directory, module))
    except FileExistsError:
        pass
    path = os.path.join(directory, module, r.__name__ + '.json')
    res = r(*args, **kwargs)
    with open(path, 'a+') as f:
        f.seek(0)
        f.truncate()
        j = json.dumps(res).encode().decode("unicode-escape")
        f.write(j)


payloads = {
    'add_items': {'50497432': 1},
    'delete_items': '50497432',
    'purchase_info': '111111111'
}

class_args = {
    'OrderCapture': ("101000")
}


def save_responses_for_class(cl, token):
    for s in cl.__dict__:
        if cl.__name__ in class_args:
            cur_cl = cl(token, class_args[cl.__name__])
        else:
            cur_cl = cl(token)
        if not re.match(r'_', s) and s != 'error_handler':
            f = getattr(cur_cl, s)
            if s in payloads:
                save_json(f, payloads[s])
            else:
                save_json(f)


def main():
    Cart(token).add_items(payloads['add_items'])
    for cl in OrderCapture, Cart:
        save_responses_for_class(cl, token)
    save_responses_for_class(Profile, auth_token)


if __name__ == '__main__':
    main()
