from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect
from .message.models import MessageOut


class ChatRoomManager:

    def __init__(self):
        self.global_websockets: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.global_websockets[user_id] = websocket
        print(f"User #{user_id} connected successfully.")

    async def disconnect_global(self, user_id: int):
        websocket = self.global_websockets.pop(user_id, None)
        if websocket:
            await websocket.close()
            print(f"User #{user_id} global websocket closed.")

    async def broadcast(self, receiver_id: int, message: MessageOut):
        websocket = self.global_websockets.get(receiver_id)
        if websocket and websocket.client_state.name == "CONNECTED":
            try:
                await websocket.send_text(message.model_dump_json())
                print(f"[Direct Message] Sent to user #{receiver_id}")
            except WebSocketDisconnect:
                print(f"[Direct Message] WebSocket of receiver #{receiver_id} disconnected.")
                await self.disconnect_global(receiver_id)

    async def broadcast_group_v2(self, message: MessageOut, member_ids: list[int]):
        for member_id in member_ids:
            websocket = self.global_websockets.get(member_id)
            if websocket and websocket.client_state.name == "CONNECTED":
                try:
                    await websocket.send_text(message.model_dump_json())
                    print(f"[Group Message] Sent to user #{member_id}")
                except WebSocketDisconnect:
                    print(f"[Group Message] WebSocket of user #{member_id} disconnected.")
                    await self.disconnect_global(member_id)


# Singleton instance of the manager
manager = ChatRoomManager()


# Dependency for injection
def getChatRoomsManager():
    return manager
