from django.urls import re_path
from .consumers import *

websocket_urlpatterns = [
    re_path(r'ws/user/(?P<user_id>[0-9]+)/', RoomConsumer.as_asgi()),  
]
