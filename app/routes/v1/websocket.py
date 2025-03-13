from typing import List
from fastapi import WebSocket
from schemas.message_base import MessageBaseExtended


class ChatRoomManager():
    def __init__(self):
        self.chat_rooms: dict[int, List[WebSocket]] = {}

    async def connect(self, conversation_id: int, websocket: WebSocket):
        await websocket.accept()
        if conversation_id in self.chat_rooms:
            self.chat_rooms[conversation_id].append(websocket)
        self.chat_rooms[conversation_id] = [websocket]
        

    def disconnect(self, conversation_id: int, websocket: WebSocket):
        if conversation_id in self.chat_rooms:
            self.chat_rooms[conversation_id].remove(websocket)
            if len(self.chat_rooms[conversation_id]) == 0:
                del self.chat_rooms[conversation_id]

    async def broadcast(self, conversation_id : int, message: MessageBaseExtended):
        if conversation_id in self.chat_rooms:
            for websocket in self.chat_rooms[conversation_id]:
                print(message)
                websocket.send_text(message)


manager = ChatRoomManager()

def getChatRoomsManager():
    return manager


