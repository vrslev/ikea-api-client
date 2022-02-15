from ikea_api._endpoints.auth import get_guest_token
from new.constants import Constants
from new.core import run
from new.endpoints import cart

token = get_guest_token()
endp = cart.API(Constants(), token=token).show()
print(run(endp))
