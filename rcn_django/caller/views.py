from django.http import HttpResponse
from django.shortcuts import render

from caller.consumer import CallerConsumer


def index(request):
    return render(request, 'index.html', context={'text': 'hello world'})


def acceptCall(request, phone):
    message = {"number": phone, "status": "Accepted"}
    cc = CallerConsumer()
    cc.event_trigger(message, ajax=True)
    return HttpResponse("Accepted "+phone)
