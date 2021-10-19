from django.urls import path

from caller.consumer import CallerConsumer

ws_urlpatterns = [
    path('ws/get_callers/', CallerConsumer.as_asgi())
]