import json
import os
import re

from ikea_api import Cart, OrderCapture

token = os.environ["TOKEN"]

payloads = {
    "add_items": {"90428328": 1},
    "update_items": {"90428328": 5},
    "remove_items": ["90428328"],
}

class_args = {"OrderCapture": ("101000")}

functions_to_skip = ["error_handler", "copy_items", "set_coupon"]


def save_json(r, *args, **kwargs):
    directory = "response_examples"
    try:
        os.mkdir(directory)
    except FileExistsError:
        pass
    module = re.findall(r".([^.]+$)", r.__module__)[0]
    try:
        os.mkdir(os.path.join(directory, module))
    except FileExistsError:
        pass
    path = os.path.join(directory, module, r.__name__ + ".json")
    res = r(*args, **kwargs)
    with open(path, "a+") as f:
        f.seek(0)
        f.truncate()
        j = json.dumps(res).encode().decode("unicode-escape")
        f.write(j)


def save_responses_for_class(cl, token):
    for s in cl.__dict__:
        if cl.__name__ in class_args:
            cur_cl = cl(token, class_args[cl.__name__])
        else:
            cur_cl = cl(token)
        if not re.match(r"_", s) and s not in functions_to_skip:
            f = getattr(cur_cl, s)
            if s in payloads:
                save_json(f, payloads[s])
            else:
                save_json(f)


def main():
    Cart(token).add_items(payloads["add_items"])
    for cl in OrderCapture, Cart:
        save_responses_for_class(cl, token)


if __name__ == "__main__":
    main()
