from django.urls import path , include
from .views import home_view, explain_repo_view

urlpatterns = [
    path('', home_view, name='home'),
    path('explain_repo/', explain_repo_view, name='explain_repo'),
]
