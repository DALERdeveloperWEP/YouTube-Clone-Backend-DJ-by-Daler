import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from interactions.models import Comment
from .models import Video

User = get_user_model()


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.video_id = int(self.scope["url_route"]["kwargs"]["video_id"])
        self.room_group_name = f"comments_{self.video_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send_json({
            "type": "connection",
            "payload": {"message": "Connected to comments", "video_id": self.video_id}
        })

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            content = (data.get("content") or "").strip()
            parent_id = data.get("parent_id")

            if not content:
                return await self.send_json({
                    "type": "error",
                    "payload": {"message": "Content cannot be empty"}
                })

            if self.scope["user"].is_anonymous:
                return await self.send_json({
                    "type": "error",
                    "payload": {"message": "You must be logged in to comment"}
                })

            comment = await self.create_comment(
                user_id=self.scope["user"].id,
                video_id=self.video_id,
                content=content,
                parent_id=parent_id,
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "comment_message",
                    "payload": comment,
                }
            )

        except Exception as e:
            await self.send_json({
                "type": "error",
                "payload": {"message": str(e)}
            })

    async def comment_message(self, event):
        await self.send_json({
            "type": "comment",
            "payload": event["payload"]
        })

    async def send_json(self, data: dict):
        await self.send(text_data=json.dumps(data))

    @database_sync_to_async
    def create_comment(self, user_id: int, video_id: int, content: str, parent_id=None):
        try:
            user = User.objects.get(id=user_id)
            video = Video.objects.get(id=video_id)
        except ObjectDoesNotExist:
            # bu exception WS receive’da errorga tushadi
            raise Exception("Video or user not found")

        parent = None
        if parent_id:
            parent = Comment.objects.filter(id=parent_id, video_id=video_id).first()

        c = Comment.objects.create(
            user=user,
            video=video,
            content=content,
            parent=parent,
        )

        return {
            "id": c.id,
            "content": c.content,
            "user": c.user.id,
            "username": getattr(c.user, "username", str(c.user)),
            "created_at": c.created_at.isoformat(),
            "parent_id": c.parent_id,
            "video_id": c.video_id,
        }