from app.db.mongo import mongo_db
from app.models.mongo.models import ConversationModel
from app.repositories.conversation_repository import ConversationRepository
from app.schemas.conversation import ConversationResponse
from app.services._service import BaseService


class ConversationService(BaseService):
    def __init__(self) -> None:
        self.repository = ConversationRepository(ConversationModel, "conversations")
        self.response_schema = ConversationResponse
        self.db_session_factory = mongo_db
