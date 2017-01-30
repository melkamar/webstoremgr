import requests


class Store:
    """
    Base class representing any webstore.

    """

    def __init__(self, session=None):
        """

        Args:
            session(requests.Session): If supplied, this session will be used for all internet communication.
             If none, a new session if created.
        """
        super().__init__()
        self.session = session or requests.Session()
