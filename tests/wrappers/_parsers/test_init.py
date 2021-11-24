from ikea_api._constants import Constants
from ikea_api.wrappers._parsers import translate_from_dict


def test_translate_no_value():
    Constants.LANGUAGE_CODE = "nolang"
    assert translate_from_dict({}, "v") == "v"
    assert translate_from_dict({"en": {}}, "v") == "v"
    Constants.LANGUAGE_CODE = "ru"


def test_translate_with_value():
    Constants.LANGUAGE_CODE = "nolang"
    assert (
        translate_from_dict({"en": {"v": "en v"}, "nolang": {"v": "nolang v"}}, "v")
        == "nolang v"
    )
    Constants.LANGUAGE_CODE = "ru"
