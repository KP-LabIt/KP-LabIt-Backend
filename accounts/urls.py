from django.urls import path
from .views import get_init, login, change_password

urlpatterns = [
    path("", get_init, name="get_init"),
    path("login/", login, name="login"),
    path("change_password/", change_password, name="change_password"),

]