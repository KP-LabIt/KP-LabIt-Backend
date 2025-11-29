from django.urls import path
from .views import get_init, login

urlpatterns = [
    path("", get_init, name="get_init"),
    path("login/", login, name="login"),
]