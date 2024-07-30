from .consumers import ChatConsumer
from django.urls import path, re_path
from . import views

websocket_urlpatterns = [
    path('ws/chat/', ChatConsumer.as_asgi()),
]

urlpatterns = [
    path('get-messages-by-user/', views.get_messages_by_user, name='get-messages-by-user')
]