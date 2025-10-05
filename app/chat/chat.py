import socketio
from fastapi.encoders import jsonable_encoder

from app.auth.authorization import get_current_user_from_token
from app.config import settings
from app.schemas.message import MessageContent, MessageCreate
from app.services.conversation import ConversationService
from app.services.message import MessageService


class ChatServer:
    def __init__(self) -> None:
        self._sio = socketio.AsyncServer(
            async_mode=settings.socket.ASYNC_MODE, cors_allowed_origins=[]
        )
        self._setup_handlers()

    def create_app(self) -> socketio.ASGIApp:
        return socketio.ASGIApp(socketio_server=self._sio, socketio_path="")

    def _setup_handlers(self):
        self._sio.on("connect", self._on_connect)
        self._sio.on("disconnect", self._on_disconnect)
        self._sio.on("send_message", self._on_send_message)
        self._sio.on("join_conversation", self._on_join_conversation)

    def _authenticate_user(self, environ: dict):
        token = environ.get("HTTP_AUTHORIZATION")
        if not token:
            raise ConnectionRefusedError("Authentication failed")
        return get_current_user_from_token(token)

    async def _on_connect(self, sid: str, environ: dict) -> None:
        user = self._authenticate_user(environ)
        await self._sio.save_session(sid, {"user": user})

    async def _on_disconnect(self, sid: str, environ: dict) -> None:
        await self._sio.get_session(sid)

    async def _on_send_message(self, sid: str, conversation_id: str, body: str):
        session = await self._sio.get_session(sid)
        user = session["user"]

        conversation = await ConversationService().find_one(
            id=conversation_id
        )

        if not conversation:
            await self._sio.emit("error", {"message": "Conversation not found"}, to=sid)
            return

        if user.id not in conversation.participants:
            await self._sio.emit("error", {"message": "Access denied"}, to=sid)
            return

        payload = MessageCreate(
            authorId=user.id,
            conversationId=conversation.id,
            content=MessageContent(type="TEXT", text=body)
        )
        message = await MessageService().create(payload)
        
        await self._sio.emit(
            "new_message",
            jsonable_encoder(message),
            room=f"conversation_{conversation_id}",
        )

    async def _on_join_conversation(self, sid: str, conversation_id: str):
        session = await self._sio.get_session(sid)
        user = session["user"]

        conversation = await ConversationService().find_one(
            id=conversation_id
        )
        if not conversation:
            await self._sio.emit("error", {"message": "Conversation not found"}, to=sid)
            return

        if user.id not in conversation.participants:
            await self._sio.emit("error", {"message": "Access denied"}, to=sid)
            return

        await self._sio.enter_room(sid, f"conversation_{conversation_id}")
        await self._sio.emit(
            "joined_conversation", {"conversation_id": str(conversation_id)}, to=sid
        )
