import requests


class Store:
    def __init__(self, session=None):
        super().__init__()
        self.session = session or requests.Session()
