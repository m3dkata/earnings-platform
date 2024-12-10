from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

class UserActivityConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
            
        await self.channel_layer.group_add("user_activity", self.channel_name)
        await self.accept()
        
        has_profile = await self.has_employee_profile(self.user)
        if has_profile:
            await self.update_employee_status(True)
            await self.channel_layer.group_send(
                "user_activity",
                {
                    "type": "user_status",
                    "user_id": self.user.id,
                    "status": "online"
                }
            )

    async def disconnect(self, close_code):
        if self.scope["user"].is_authenticated:
            await self.update_employee_status(False)
            await self.channel_layer.group_send(
                "user_activity",
                {
                    "type": "user_status",
                    "user_id": self.scope["user"].id,
                    "status": "offline"
                }
            )
        await self.channel_layer.group_discard("user_activity", self.channel_name)

    async def user_status(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def has_employee_profile(self, user):
        return hasattr(user, 'employee_profile')

    @database_sync_to_async
    def update_employee_status(self, is_online):
        if hasattr(self.user, 'employee_profile'):
            # print(f"Updating status for user {self.user.id} to {is_online}")
            self.user.employee_profile.is_online = is_online
            self.user.employee_profile.save()
            # print(f"Status after save: {self.user.employee_profile.is_online}")
