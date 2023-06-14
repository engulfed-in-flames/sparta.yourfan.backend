import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from chat import consumers as chat
from community import consumers as commu

import jwt
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from django.conf import settings
from django.shortcuts import get_object_or_404

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourfan.settings')

@database_sync_to_async
def get_user_or_anonymous(token):
    try:
        User = get_user_model()
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = get_object_or_404(User,email=payload["email"])
        return user
    except user.DoesNotExist:
        print("Error: No user found with the email")
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        params = parse_qs(scope["query_string"].decode("utf8"))
        if "token" in params:
            token = params["token"][0]
            user = await get_user_or_anonymous(token)
            from django.contrib.auth.models import AnonymousUser
            if user is None:
                user = AnonymousUser()
            scope['user'] = user
        return await super().__call__(scope, receive, send)


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        URLRouter([
            path('ws/chat/<board>/', chat.ChatConsumer.as_asgi()),
            path('ws/alert/', commu.NotificationConsumer.as_asgi()),
        ]),
    ),
})
