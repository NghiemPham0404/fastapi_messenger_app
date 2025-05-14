from typing import List
from fastapi import WebSocket
from ...schemas.message_base import MessageOut
from ...encrypt_message import decrypt_message


class ChatRoomManager():
    def __init__(self):
        self.global_websockets : dict[int, WebSocket] = {}
        self.chat_rooms: dict[int, List[WebSocket]] = {}

    async def connect(self, conversation_id: int, user_id : int, websocket: WebSocket):
        await websocket.accept()
        print(f"websocket {conversation_id} connecting ")
        self.chat_rooms.setdefault(conversation_id, []).append(websocket)
        self.global_websockets[user_id] = websocket
        if conversation_id in self.chat_rooms:
            print(f"conversation websocket ${conversation_id} connect sucessfully")
        else:
            print(f"conversation websocket ${conversation_id} connect sucessfully")

    def disconnect(self, conversation_id: int, websocket: WebSocket):
        if conversation_id in self.chat_rooms:
            self.chat_rooms[conversation_id].remove(websocket)
            if len(self.chat_rooms[conversation_id]) == 0:
                del self.chat_rooms[conversation_id]

    def disconnect_global(self, user_id, websocket:WebSocket):
        for room in self.chat_rooms.values():
            if websocket in room:
                room.remove(websocket)

        self.global_websockets[user_id].close()
        self.global_websockets.pop(user_id)

    async def broadcast(self, conversation_id : int, message: MessageOut):
        if conversation_id in self.chat_rooms:
            print(f"conversation websocket ${conversation_id} exist")
            for websocket in self.chat_rooms[conversation_id]:
                print(message.content)
                await websocket.send_text(message.model_dump_json())
        else:
            print(f"conversation websocket ${conversation_id} doesn't exist") 

manager = ChatRoomManager()

def getChatRoomsManager():
    return manager


