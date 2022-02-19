from ikea_api.constants import Constants
from ikea_api.utils import translate_from_dict


def test_translate_no_value():
    constants = Constants(language="nolang")
    assert translate_from_dict(constants, {}, "v") == "v"
    assert translate_from_dict(constants, {"en": {}}, "v") == "v"


def test_translate_with_value():
    constants = Constants(language="nolang")
    assert (
        translate_from_dict(
            constants, {"en": {"v": "en v"}, "nolang": {"v": "nolang v"}}, "v"
        )
        == "nolang v"
    )
