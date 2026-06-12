from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_str: str):
    """Validate a JWT access token and return the associated user."""
    try:
        token = AccessToken(token_str)
        user_id = token.get("user_id")
        if not user_id:
            return AnonymousUser()
        user = User.objects.select_related("guard_profile").get(id=user_id)
        return user
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Django Channels middleware that authenticates WebSocket connections
    using a JWT token passed as a query parameter: ?token=<access_token>

    This is the only viable method for WebSocket auth since browsers
    cannot set custom headers on WS handshake requests.
    """

    async def __call__(self, scope, receive, send):
        # Parse query string for token
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_list = params.get("token", [])

        if token_list:
            scope["user"] = await get_user_from_token(token_list[0])
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """Convenience wrapper — wrap inner application with JWTAuthMiddleware."""
    return JWTAuthMiddleware(inner)
