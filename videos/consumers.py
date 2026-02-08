import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from ..interactions.models import Comment
from .models import Video

User = get_user_model()


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.video_id = self.scope["url_route"]["kwargs"]["video_id"]
        self.room_group_name = f"comments_{self.video_id}"
        
        # DEBUG: Print connection info
        print(f"🔌 WebSocket connection attempt for video {self.video_id}")
        print(f"👤 User: {self.scope['user']}")
        print(f"🔒 Is authenticated: {self.scope['user'].is_authenticated}")

        # IMPORTANT: Accept connection first, then check auth
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to comments'
        }))

    async def disconnect(self, close_code):
        print(f"🔌 WebSocket disconnected: {close_code}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            content = (data.get("content") or "").strip()
            parent_id = data.get("parent_id")

            print(f"📨 Received: {content}")

            if not content:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Content cannot be empty'
                }))
                return

            # Check authentication
            if self.scope["user"].is_anonymous:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'You must be logged in to comment'
                }))
                return

            # Create comment
            comment = await self.create_comment(
                user_id=self.scope["user"].id,
                video_id=int(self.video_id),
                content=content,
                parent_id=parent_id,
            )

            # Broadcast to all users in this video's room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "comment_message",
                    "comment": {
                        "id": comment["id"],
                        "content": comment["content"],
                        "user": comment["user"],
                        "username": comment["username"],
                        "created_at": comment["created_at"],
                        "parent_id": comment["parent_id"],
                    },
                }
            )

        except Exception as e:
            print(f"❌ Error in receive: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def comment_message(self, event):
        """Receive message from room group and send to WebSocket"""
        await self.send(text_data=json.dumps(event["comment"]))

    @database_sync_to_async
    def create_comment(self, user_id: int, video_id: int, content: str, parent_id=None):
        user = User.objects.get(id=user_id)
        video = Video.objects.get(id=video_id)

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
        }