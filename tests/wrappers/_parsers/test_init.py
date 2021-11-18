from ikea_api._constants import Constants
from ikea_api.wrappers._parsers import translate


def test_translate_no_value():
    Constants.LANGUAGE_CODE = "nolang"
    assert translate({}, "v") == "v"
    assert translate({"en": {}}, "v") == "v"
    Constants.LANGUAGE_CODE = "ru"


def test_translate_with_value():
    Constants.LANGUAGE_CODE = "nolang"
    assert (
        translate({"en": {"v": "en v"}, "nolang": {"v": "nolang v"}}, "v") == "nolang v"
    )
    Constants.LANGUAGE_CODE = "ru"
