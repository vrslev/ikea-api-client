from new.constants import Constants
from new.wrappers.parsers.utils import translate_from_dict


def test_translate_no_value(constants: Constants):
    constants.language = "nolang"
    assert translate_from_dict({}, "v") == "v"
    assert translate_from_dict({"en": {}}, "v") == "v"
    constants.language = "ru"


def test_translate_with_value():
    Constants.LANGUAGE_CODE = "nolang"
    assert (
        translate_from_dict({"en": {"v": "en v"}, "nolang": {"v": "nolang v"}}, "v")
        == "nolang v"
    )
    Constants.LANGUAGE_CODE = "ru"
