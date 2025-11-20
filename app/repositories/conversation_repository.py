from app.models.mongo.models import ConversationModel
from app.repositories.mongo_repository import MongoDBRepository
from app.schemas.conversation import ConversationCreate, ConversationUpdate


class ConversationRepository(
    MongoDBRepository[ConversationModel, ConversationCreate, ConversationUpdate]
): ...
