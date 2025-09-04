from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import uuid
from typing import Dict, List
import logging
import os

app = FastAPI()

# CORS middleware (no credentials with wildcard origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for active connections and rooms
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, List[str]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected")

    def disconnect(self, user_id: str) -> List[str]:
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Remove user from all rooms and collect rooms to notify
        rooms_left: List[str] = []
        for room_id in list(self.rooms.keys()):
            users = self.rooms.get(room_id, [])
            if user_id in users:
                users.remove(user_id)
                rooms_left.append(room_id)
                if not users:
                    # Remove empty room
                    del self.rooms[room_id]
        
        logger.info(f"User {user_id} disconnected")
        return rooms_left

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))

    async def broadcast_to_room(self, message: dict, room_id: str, exclude_user: str = None):
        if room_id in self.rooms:
            for user_id in self.rooms[room_id]:
                if user_id != exclude_user and user_id in self.active_connections:
                    await self.active_connections[user_id].send_text(json.dumps(message))

    def create_room(self, room_id: str, user_id: str):
        if room_id not in self.rooms:
            self.rooms[room_id] = []
        if user_id not in self.rooms[room_id]:
            self.rooms[room_id].append(user_id)
        logger.info(f"User {user_id} joined room {room_id}")

    def leave_room(self, room_id: str, user_id: str):
        if room_id in self.rooms and user_id in self.rooms[room_id]:
            self.rooms[room_id].remove(user_id)
            if not self.rooms[room_id]:
                del self.rooms[room_id]
        logger.info(f"User {user_id} left room {room_id}")

manager = ConnectionManager()

# Models
class CallRequest(BaseModel):
    caller_id: str
    callee_id: str

class MessageData(BaseModel):
    type: str
    room_id: str = None
    data: dict = None

# Serve the main HTML file
@app.get("/")
async def read_root():
    return FileResponse('index.html')

# Serve test page
@app.get("/test")
async def read_test():
    return FileResponse('test_connection.html')

@app.get("/api/generate-room")
async def generate_room():
    room_id = str(uuid.uuid4())
    return {"room_id": room_id}

@app.get("/api/rooms")
async def list_rooms():
    """Вернуть список активных комнат и число участников в каждой."""
    return {
        "rooms": [
            {"id": room_id, "count": len(users)}
            for room_id, users in manager.rooms.items()
        ]
    }

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "join_room":
                room_id = message.get("room_id")
                # список участников до добавления текущего
                existing_users = list(manager.rooms.get(room_id, []))
                manager.create_room(room_id, user_id)

                # Отправляем список текущих участников вошедшему
                await manager.send_personal_message({
                    "type": "room_users",
                    "room_id": room_id,
                    "users": existing_users
                }, user_id)
                
                # Notify others in the room
                await manager.broadcast_to_room({
                    "type": "user_joined",
                    "user_id": user_id,
                    "room_id": room_id
                }, room_id, exclude_user=user_id)
                
            elif message_type == "leave_room":
                room_id = message.get("room_id")
                manager.leave_room(room_id, user_id)
                
                # Notify others in the room
                await manager.broadcast_to_room({
                    "type": "user_left",
                    "user_id": user_id,
                    "room_id": room_id
                }, room_id)
                
            elif message_type == "offer":
                room_id = message.get("room_id")
                to_user = message.get("to_user")
                payload = {
                    "type": "offer",
                    "offer": message.get("offer"),
                    "from_user": user_id,
                    "room_id": room_id
                }
                if to_user:
                    payload["to_user"] = to_user
                    await manager.send_personal_message(payload, to_user)
                else:
                    await manager.broadcast_to_room(payload, room_id, exclude_user=user_id)
                
            elif message_type == "answer":
                room_id = message.get("room_id")
                to_user = message.get("to_user")
                payload = {
                    "type": "answer",
                    "answer": message.get("answer"),
                    "from_user": user_id,
                    "room_id": room_id
                }
                if to_user:
                    payload["to_user"] = to_user
                    await manager.send_personal_message(payload, to_user)
                else:
                    await manager.broadcast_to_room(payload, room_id, exclude_user=user_id)
                
            elif message_type == "ice_candidate":
                room_id = message.get("room_id")
                to_user = message.get("to_user")
                payload = {
                    "type": "ice_candidate",
                    "candidate": message.get("candidate"),
                    "from_user": user_id,
                    "room_id": room_id
                }
                if to_user:
                    payload["to_user"] = to_user
                    await manager.send_personal_message(payload, to_user)
                else:
                    await manager.broadcast_to_room(payload, room_id, exclude_user=user_id)
                
            elif message_type == "hangup":
                room_id = message.get("room_id")
                to_user = message.get("to_user")
                payload = {
                    "type": "hangup",
                    "from_user": user_id,
                    "room_id": room_id
                }
                if to_user:
                    payload["to_user"] = to_user
                    await manager.send_personal_message(payload, to_user)
                else:
                    await manager.broadcast_to_room(payload, room_id, exclude_user=user_id)
                
    except WebSocketDisconnect:
        # On unexpected disconnect, remove user and notify rooms
        rooms_left = manager.disconnect(user_id)
        for room_id in rooms_left:
            await manager.broadcast_to_room({
                "type": "user_left",
                "user_id": user_id,
                "room_id": room_id
            }, room_id)

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Проверяем наличие SSL сертификатов
    ssl_keyfile = "ssl/key.pem"
    ssl_certfile = "ssl/cert.pem"
    
    if os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
        print("🔐 Запуск с HTTPS...")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info",
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile
        )
    else:
        print("⚠️ Запуск без HTTPS (только localhost для камеры)")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
