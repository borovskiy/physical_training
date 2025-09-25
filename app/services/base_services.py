import logging


class BaseServices:
    def __init__(self):
        self.log = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {"component": self.__class__.__name__}
        )
