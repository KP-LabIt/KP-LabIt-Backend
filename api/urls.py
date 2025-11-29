from django.urls import path
from .views import get_data, get_init, post_test, login

urlpatterns = [
    path("", get_init, name="get_init"),
    path("data/", get_data, name="get_data"),
    path("data/create/", post_test, name="post_test"),
    path("login/", login, name="login"),
]