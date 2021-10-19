from django.urls import path

from caller.views import index, acceptCall

urlpatterns = [
    path('', index),
    path('acceptCall/<str:phone>/', acceptCall, name='acceptCall')
]
