import logging
from uuid import UUID

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: dict[UUID, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: UUID):
        """
        Принять новое WebSocket-соединение и сохранить его.
        """
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(
            f"WebSocket-соединение для пользователя {user_id} установлено.", flush=True
        )

    def disconnect(self, user_id: UUID):
        """
        Удалить WebSocket-соединение при разрыве.
        """
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(
                f"WebSocket-соединение для пользователя {user_id} разорвано.",
                flush=True,
            )

    async def send_personal_message(self, user_id: UUID, message: str):
        """
        Отправить сообщение конкретному пользователю, если он онлайн.
        """
        websocket = self.active_connections.get(user_id)
        if websocket:
            logger.info(
                f"Отправка сообщения пользователю {user_id}: {message}"
            )
            await websocket.send_text(message)
        else:
            logger.info(
                f"Пользователь {user_id} не подключен, сообщение не отправлено."
            )

    async def broadcast(self, message: str):
        """
        Отправить сообщение всем подключённым пользователям.
        Если потребуется отправлять всем.
        """
        for connection in self.active_connections.values():
            await connection.send_text(message)


manager = WebSocketConnectionManager()
