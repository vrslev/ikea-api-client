import re
from typing import Union

from .errors import WrongZipCodeError


def validate_zip_code(zip_code: Union[str, int]):  # TODO: MOve to purchases
    if len(re.findall(r"[^0-9]", str(zip_code))) > 0:
        raise WrongZipCodeError(zip_code)
