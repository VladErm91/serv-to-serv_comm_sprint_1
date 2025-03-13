import logging
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websockets_manager import manager

router = APIRouter()

logger = logging.getLogger(__name__)


@router.websocket("/ws/push/{user_id}")
async def websocket_push_notifications(websocket: WebSocket, user_id: UUID):
    """
    Веб-сокет для отправки push-уведомлений пользователю с указанным user_id.
    """
    await manager.connect(websocket, user_id)
    try:
        logger.info(f"Подключение WebSocket для {user_id} установлено.")
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(user_id, f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        logger.info(f"Подключение WebSocket для {user_id} закрыто.")
