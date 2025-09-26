import logging

from app.core.config import settings
from app.services.rabbit_service import RabbitClientStateless


class BaseServices:
    def __init__(self):
        self.log = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {"component": self.__class__.__name__}
        )
        self.rabbit_service = RabbitClientStateless(settings.AMQP_URL, default_queue="orders")
