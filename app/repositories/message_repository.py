from app.models.mongo.models import MessageModel
from app.repositories.mongo_repository import MongoDBRepository
from app.schemas.message import MessageCreate, MessageUpdate


class MessageRepository(
    MongoDBRepository[MessageModel, MessageCreate, MessageUpdate]
): ...
