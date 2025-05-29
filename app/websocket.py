from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect
from .message.models import MessageOut
from .encrypt_message import decrypt_message
import asyncio


class ChatRoomManager:
    def __init__(self):
        self.global_websockets: Dict[int, WebSocket] = {}
        self.chat_rooms: Dict[int, List[int]] = {}

    async def connect(self, group_id: int, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.global_websockets[user_id] = websocket
        self.chat_rooms.setdefault(group_id, [])

        if user_id not in self.chat_rooms[group_id]:
            self.chat_rooms[group_id].append(user_id)

        print(f"User #{user_id} connected to group #{group_id} successfully.")

    def disconnect_group(self, group_id: int, user_id: int):
        if group_id in self.chat_rooms and user_id in self.chat_rooms[group_id]:
            self.chat_rooms[group_id].remove(user_id)
            if not self.chat_rooms[group_id]:
                del self.chat_rooms[group_id]
            print(f"User #{user_id} disconnected from group #{group_id}.")

    async def disconnect_global(self, user_id: int):
        websocket = self.global_websockets.pop(user_id, None)
        if websocket:
            await websocket.close()
            print(f"User #{user_id} global websocket closed.")

        # Remove user from any group they might belong to
        for group_id in list(self.chat_rooms.keys()):
            if user_id in self.chat_rooms[group_id]:
                self.chat_rooms[group_id].remove(user_id)
                if not self.chat_rooms[group_id]:
                    del self.chat_rooms[group_id]

    async def broadcast_group(self, group_id: int, message: MessageOut):
        if group_id not in self.chat_rooms:
            print(f"[broadcast_group] Group #{group_id} does not exist.")
            return

        print(f"[broadcast_group] Broadcasting to group #{group_id}")

        for user_id in self.chat_rooms[group_id]:
            websocket = self.global_websockets.get(user_id)
            if websocket:
                try:
                    await websocket.send_text(message.model_dump_json())
                except WebSocketDisconnect:
                    print(f"WebSocket for user #{user_id} in group #{group_id} disconnected.")
                    await self.disconnect_global(user_id)

    async def broadcast(self, receiver_id: int, message: MessageOut):
        websocket = self.global_websockets.get(receiver_id)
        if websocket:
            try:
                await websocket.send_text(message.model_dump_json())
            except WebSocketDisconnect:
                print(f"WebSocket for receiver #{receiver_id} disconnected.")
                await self.disconnect_global(receiver_id)


# Singleton instance of the manager
manager = ChatRoomManager()


# Dependency for injection
def getChatRoomsManager():
    return manager
