from django.urls import path
from .views import get_init, login, change_password, CustomUserViewSet
from djoser.views import UserViewSet

urlpatterns = [
    path("", get_init, name="get_init"),
    path("login/", login, name="login"),
    path("change_password/", change_password, name="change_password"),
    # tieto 2 endpointy dole su importnute z djoser knižnice takže logiku netreba riešiť. POZOR, TIETO ENDPOINTY NIE SÚ EŠTE PREPOJENÉ S FRONTENDOM. TREBA DOPLNIŤ..
    # Do frontendu treba pridať nejaký text v login page že "Zabudli ste heslo?", a ten text ťa presmeruje na page ktory je dostupny pre kazdeho, nie je protected.
    # Ten page by mal mať nekajy formular, kde treba zadať mail(inšpiracia sa keď tak može zobrať z online školy, tam je na login page tiež taky text a page)
    # Keď sa zadá email, tak by sa mal poslať request na ten reset_password endpoint, ktory očakáva mail( Payload: { "email": "<user_email>" } ), Ak e-mail neexistuje, endpoint vráti 400 Bad Request, inač vráti 204 No Content, ale mal by poslať mail, ktory bude obsahovať reset link(vie sa použiť mailgun na posielanie asi.)
    # Ten link by mal vyzerat nejako takto -> <frontend_url>#/reset_password/<uid>/<token>. Na tejto page treba zadat nové heslo. Potom sa pošle request na ten druhy endpoint.
    # reset_password_confirm endpoint očakáva uid, token a nové heslo( Payload: { "uid": "...", "token": "...", "new_password": "..." } ). keď je uid a token valid, tak sa uloží nové heslo.
    # Cielom tohto je, aby si mohli studenti zmenit heslo, lebo teraz tam maju v podstate placeholder heslo, a aby sa neposielal kazdemu mail s jeho heslom, tak staci, aby si klikol na ten odkaz, vyplnil jeho mail, na maile sa mu to otvori, zmeni heslo a hotovo. ked bude prihlaseny, tak si kludne vie stale zmenit heslo v jeho profile.
    path("reset_password/", UserViewSet.as_view({"post": "reset_password"}), name="reset_password"),
    path("reset_password_confirm/", CustomUserViewSet.as_view({"post": "reset_password_confirm"}), name="reset_password_confirm"),
]