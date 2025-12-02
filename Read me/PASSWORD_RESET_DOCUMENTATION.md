# 🔐 Password Reset - Djoser + Mailgun

## Prehľad

- **Djoser:** Password reset logika (UID/token generovanie)
- **Anymail + Mailgun:** Email doručenie (EU region)
- **Custom:** Nastavuje must_change_password = False po resete

## Flow

1. Frontend → POST /api/accounts/reset_password/ {"email": "..."}
2. Backend → Pošle email s reset linkom cez Mailgun
3. User → Klikne link → Frontend formulár
4. Frontend → POST /api/accounts/reset_password_confirm/ {"uid", "token", "new_password"}
5. Backend → Zmení heslo + must_change_password = False

## API Endpointy

### 1. Reset Request
POST /api/accounts/reset_password/
Payload: {"email": "stanko_d@katkinpark.sk"}
Response: 204 (email odoslaný) | 400 (email neexistuje)

### 2. Reset Confirm
POST /api/accounts/reset_password_confirm/
Payload: {"uid": "MQ", "token": "...", "new_password": "NewPass123!"}
Response: 204 (heslo zmenené) | 400 (neplatný token)

## Konfigurácia

Settings (app/settings.py):
- INSTALLED_APPS = ["djoser", "anymail"]
- DJOSER = {"LOGIN_FIELD": "email", "PASSWORD_RESET_CONFIRM_URL": "reset_password/{uid}/{token}"}
- EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
- ANYMAIL = {"MAILGUN_API_KEY": os.getenv("MAILGUN_API_KEY"), "MAILGUN_SENDER_DOMAIN": "mail.simonszi.me"}

URLs (accounts/urls.py):
- path("reset_password/", UserViewSet.as_view({"post": "reset_password"}))
- path("reset_password_confirm/", CustomUserViewSet.as_view({"post": "reset_password_confirm"}))

## Frontend Integrácia

1. Forgot Password:
   fetch('/api/accounts/reset_password/', {method: 'POST', body: JSON.stringify({email})})

2. Email Link:
   http://frontend.com/#/reset_password/{uid}/{token}

3. Reset Password:
   fetch('/api/accounts/reset_password_confirm/', {method: 'POST', body: JSON.stringify({uid, token, new_password})})

## Bezpečnosť

- Token: Platný 7 dní, jednorazový
- Rate limiting: Max 3x/hodinu (odporúčané)
- HTTPS: Povinné v production
- Email v spame: Pridaj SPF/DKIM záznamy v DNS

✅ Backend kompletne nakonfigurovaný!
