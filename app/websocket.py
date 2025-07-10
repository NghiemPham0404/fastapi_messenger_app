from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect
from .message.models import MessageOut
from .encrypt_message import decrypt_message
import asyncio


class ChatRoomManager:


    def __init__(self):
        self.global_websockets: Dict[int, WebSocket] = {}
        self.group_chats: Dict[int, List[int]] = {}


    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.global_websockets[user_id] = websocket
        print(f"User #{user_id} connected successfully.")


    async def disconnect_global(self, user_id: int):
        websocket = self.global_websockets.pop(user_id, None)
        if websocket:
            await websocket.close()
            print(f"User #{user_id} global websocket closed.")

        # Remove user from any group they might belong to
        for group_id in list(self.group_chats.keys()):
            if user_id in self.group_chats[group_id]:
                self.group_chats[group_id].remove(user_id)
                if not self.group_chats[group_id]:
                    del self.group_chats[group_id]


    def join_group(self, user_id : int, group_id: int):
        self.group_chats.setdefault(group_id, [])
        if group_id in self.group_chats:
            if user_id not in self.group_chats[group_id]:
                self.group_chats[group_id].append(user_id)
                print(f"User #{user_id} connected to group #${group_id} successfully")
        else:
            print(f"group #{group_id} not exist and create unsucessfully")


    def leave_group(self, user_id: int, group_id: int):
        if group_id in self.group_chats and user_id in self.group_chats[group_id]:
            self.group_chats[group_id].remove(user_id)
            print(f"User #{user_id} disconnected from group #{group_id}.")
            if not self.group_chats[group_id]:
                del self.group_chats[group_id]


    async def broadcast(self, receiver_id: int, message: MessageOut):
        websocket = self.global_websockets.get(receiver_id)
        if websocket and websocket.client_state.name == "CONNECTED":
            try:
                await websocket.send_text(message.model_dump_json())
                print(f"[Direct Message] Sent to user #{receiver_id}")
            except WebSocketDisconnect:
                print(f"[Direct Message]WebSocket of receiver #{receiver_id} disconnected.")
                await self.disconnect_global(receiver_id)


    async def broadcast_group(self, group_id: int, message: MessageOut):
        if group_id not in self.group_chats:
            print(f"[Group Message] Group #{group_id} does not exist.")
            return

        print(f"[Group Message] Sending to group #{group_id} users: {message.user_id}")

        for user_id in self.group_chats[group_id]:
            websocket = self.global_websockets.get(user_id)
            if websocket and websocket.client_state.name == "CONNECTED":
                try:
                    await websocket.send_text(message.model_dump_json())
                except WebSocketDisconnect:
                    await self.disconnect_global(user_id)


# Singleton instance of the manager
manager = ChatRoomManager()


# Dependency for injection
def getChatRoomsManager():
    return manager
