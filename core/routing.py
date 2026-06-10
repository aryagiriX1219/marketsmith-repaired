from django.urls import re_path
from .consumers import WaitingConsumer

websocket_urlpatterns = [
    re_path(r'ws/waiting/(?P<game_id>\d+)/$', WaitingConsumer.as_asgi()),
]
