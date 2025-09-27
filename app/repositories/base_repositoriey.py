import logging


class BaseRepo:
    def __init__(self):
        self.log = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {"component": self.__class__.__name__}
        )

    def get_limit(self):
        raise Exception("Not func")
