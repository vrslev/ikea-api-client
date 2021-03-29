Manage cart, check available delivery options.

Currently it is just couple of Python scripts that return raw JSON data.
I will work on improving. But if you wish to see new features or suggestions or want to contribute—feel free to open issue or commit to the project.
Note that all requests are made for Russian IKEA website. In future I'll add opportunity to change country. 
## Features
### Cart
- show
- clear
- add/delete items
- get delivery options

### Profile
- show purchase history

## Usage example
```python
from api import get_authorized_token, Cart

token = get_authorized_token(username='username', password='password')
cart = Cart(token)
cart.add_items({'30457903': 1})
deliveries = cart.get_delivery_options('your_zip_code')
print(deliveries)
```