from django.urls import path , include
from .views import home_view, chat_view

urlpatterns = [
    path('', home_view, name='home'),
    path('chat/', chat_view, name='chat'),
]
