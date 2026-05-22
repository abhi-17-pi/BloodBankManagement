import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CallAlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            "message": "Realtime alert channel is active. Click a call button to send a live alert."
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("type") == "call_alert":
            donor = data.get("donor", {})
            name = donor.get("name", "donor")
            mobile = donor.get("mobile", "unknown")
            message = f"📣 Live call alert: dialing {name} ({mobile}) now."
            await self.send(text_data=json.dumps({"message": message}))

    async def disconnect(self, close_code):
        pass
