from app.db.mongo import mongo_db
from app.models.mongo.models import MessageModel
from app.repositories.message_repository import MessageRepository
from app.schemas.message import MessageResponse
from app.services._service import BaseService


class MessageService(BaseService):
    def __init__(self) -> None:
        self.repository = MessageRepository(MessageModel, "messages")
        self.response_schema = MessageResponse
        self.db_session_factory = mongo_db
