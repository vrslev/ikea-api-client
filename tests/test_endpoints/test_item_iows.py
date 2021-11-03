from ikea_api._endpoints.item_iows import IowsItems


def test_set_initial_items():
    iows_items = IowsItems()
    iows_items._set_initial_items(["11111111", "22222222"])
    assert iows_items.items == {"11111111": False, "22222222": False}


def test_build_payload():
    items = {"11111111": False, "22222222": True}
    assert IowsItems()._build_payload(items) == "ART,11111111;SPR,22222222"
