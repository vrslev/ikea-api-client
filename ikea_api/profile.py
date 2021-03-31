import requests

from .constants import Constants


class Profile:
    def __init__(self, token):
        self.token = token
        self.endpoint = "https://purchase-history.ocp.ingka.ikea.com/graphql"
        self.headers = {
            'Origin': 'https://order.ikea.com',
            'Referer': 'https://order.ikea.com/ru/ru/purchases/',
            'Accept-Language': 'ru-ru',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'User-Agent': Constants.USER_AGENT,
            'Authorization': 'Bearer ' + self.token
        }

    def purchase_history(self):
        payload = [{
            "operationName": "Authenticated",
            "variables": {},
            "query": "query Authenticated {\n  authenticated\n}\n"
        },
            {
            "operationName": "History",
            "variables": {"take": 5, "skip": 0},
            "query": "query History($skip: Int!, $take: Int!) {\n  history(skip: $skip, take: $take) {\n    id\n    dateAndTime {\n      ...DateAndTime\n      __typename\n    }\n    status\n    storeName\n    totalCost {\n      code\n      value\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment DateAndTime on DateAndTime {\n  time\n  date\n  formattedLocal\n  formattedShortDate\n  formattedLongDate\n  formattedShortDateTime\n  formattedLongDateTime\n  __typename\n}\n"
        }
        ]
        response = requests.post(
            self.endpoint, headers=self.headers, json=payload)
        return response.json()
