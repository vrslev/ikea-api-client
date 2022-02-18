from new.constants import Constants
from new.endpoints import auth
from new.executors.requests import run

print(run(auth.API(Constants()).get_guest_token()))
