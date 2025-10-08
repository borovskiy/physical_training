import logging

from core.config import settings
from db.schemas.user_schema import UserAdminGetModelSchema
from services.rabbit_service import RabbitClientStateless
from utils.context import get_current_user
from utils.raises import _forbidden


class BaseServices:
    def __init__(self):
        self.log = logging.LoggerAdapter(
            logging.getLogger(__name__),
            {"component": self.__class__.__name__}
        )
        self.rabbit_service = RabbitClientStateless(settings.AMQP_URL, default_queue="orders")

    @staticmethod
    def check_permission(current_user: UserAdminGetModelSchema, user_id: int) -> int:
        if user_id is not None and not current_user.is_admin:
            raise _forbidden("You do not have permission to perform this action")
        return user_id if user_id is not None else get_current_user().id
