from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "test_room"
        self.room_group_name = "chat_test"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Send history AFTER accepting the connection
        await self.send_history()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type", "message")
        
        if msg_type == "join":
            username = data.get("username", "Unknown")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.system_message",
                    "message": f"{username} joined the chat",
                }
            )
            return

        message = data["message"]
        sender = data.get("sender", "anonymous")
        username = data.get("username", "Unknown")
        
        if message.strip().lower() == "clear":
            await self.clear_messages(self.room_name)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.clear_event",
                }
            )
            return

        # Save message to database
        await self.save_message(self.room_name, message, sender, username)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message,
                "sender": sender,
                "username": username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event.get("sender", "anonymous"),
            "username": event.get("username", "Unknown"),
        }))

    async def chat_clear_event(self, event):
        await self.send(text_data=json.dumps({
            "type": "clear"
        }))

    async def chat_system_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "system",
            "message": event["message"]
        }))

    async def send_history(self):
        messages = await self.get_last_10_messages(self.room_name)
        for msg in messages:
             await self.send(text_data=json.dumps({
                "message": msg['content'],
                "sender": msg['sender'],
                "username": msg['username'],
            }))

    @database_sync_to_async
    def get_last_10_messages(self, room_name):
        return [{'content': msg.content, 'sender': msg.sender, 'username': msg.username} for msg in Message.objects.filter(room_name=room_name).order_by('timestamp')[:50]]

    @database_sync_to_async
    def save_message(self, room_name, message, sender, username):
         Message.objects.create(room_name=room_name, content=message, sender=sender, username=username)

    @database_sync_to_async
    def clear_messages(self, room_name):
        Message.objects.filter(room_name=room_name).delete()
