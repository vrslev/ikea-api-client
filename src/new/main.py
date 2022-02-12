from ikea_api._endpoints.auth import get_guest_token
from new.constants import Constants
from new.endpoints.order_capture import just_get
from new.executors.requests import run

token = get_guest_token()

# print(
#     run(
#         checkout(
#             token=token, items=[{"quantity": 1, "itemNo": "30457903", "uom": "peace"}]
#         ),
#         Constants(),
#     )
# )

constants = Constants()
gen = just_get(
    token,
    items=[{"quantity": 1, "itemNo": "30457903", "uom": "peace"}],
    zip_code="164500",
)
info = next(gen)
while True:
    try:
        info = gen.send(run(info, constants))
    except StopIteration as exc:
        print(exc.value)
        break


# print(yield from gen)
# resp = run(next(gen), constants)
# print(run(gen.send(resp), constants))
# gen.send()
