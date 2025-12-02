# 🔐 JWT Token Validation System - Dokumentácia

## 📋 Obsah

1. [Prehľad](#prehľad)
2. [Rýchly štart](#rýchly-štart)
3. [Permission Classes](#permission-classes)
4. [Frontend integrácia](#frontend-integrácia)
5. [Error kódy](#error-kódy)
6. [Príklady endpointov](#príklady-endpointov)

---

## Prehľad

Backend má **kompletný systém validácie JWT tokenov** pre všetky endpointy.

### ✅ Hlavné vlastnosti:

- **5-stupňová validácia** pri každom requeste
- **Role-based access control** (študent/učiteľ/admin)
- **Token expirácia:** 8 hodín (access), 7 dní (refresh)
- **Automatická ochrana** všetkých endpointov

### 🔄 Ako to funguje:

```
1. Login → Backend vygeneruje token → Vráti { token, user }
2. Frontend uloží token
3. Každý request → Authorization: Bearer <token>
4. Backend validuje (5 krokov):
   ✓ Token prítomný?
   ✓ Token validný? (podpis)
   ✓ Nie je expirovaný?
   ✓ User_id sa zhoduje?
   ✓ Správna rola?
5. OK → Pokračuje | NOK → 401/403 error
```

---

## Rýchly štart

### 1. Login (získať token)

```bash
POST /api/accounts/login/
Content-Type: application/json

{
  "email": "horvath_a@katkinpark.sk",
  "password": "T8f$Q2m!Lp7$"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "must_change_password": true,
  "user": {
    "id": 6,
    "email": "horvath_a@katkinpark.sk",
    "role": "student"
  }
}
```

### 2. Použiť token

```bash
GET /api/accounts/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 3. Frontend príklad

```javascript
// Login
const response = await fetch('/api/accounts/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'horvath_a@katkinpark.sk',
        password: 'T8f$Q2m!Lp7$'
    })
});
const data = await response.json();
localStorage.setItem('token', data.token);

// Použiť token
const result = await fetch('/api/accounts/', {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
});
```

---

## Permission Classes

### Import:
```python
from accounts.permissions import (
    IsAuthenticatedWithValidToken,
    IsStudent,
    IsTeacher,
    IsAdmin,
    IsTeacherOrAdmin,
    IsStudentOrTeacher
)
from rest_framework.permissions import AllowAny
```

### 1. `IsAuthenticatedWithValidToken`
Akýkoľvek autentifikovaný používateľ.

```python
@api_view(["GET"])
@permission_classes([IsAuthenticatedWithValidToken])
def my_endpoint(request):
    return Response({"user": request.user.email})
```

### 2. `IsStudent`
Len študenti. Učitelia dostanú 403 s `"not_student"`.

```python
@api_view(["POST"])
@permission_classes([IsStudent])
def create_reservation(request):
    return Response({"message": "Reservation created"})
```

### 3. `IsTeacher`
Len učitelia. Študenti dostanú 403 s `"not_teacher"`.

```python
@api_view(["GET"])
@permission_classes([IsTeacher])
def get_all_reservations(request):
    return Response({"reservations": []})
```

### 4. `IsAdmin`
Len administrátori.

```python
@api_view(["DELETE"])
@permission_classes([IsAdmin])
def delete_user(request, user_id):
    return Response({"message": "Deleted"})
```

### 5. `IsTeacherOrAdmin`
Učitelia ALEBO admini.

```python
@api_view(["POST"])
@permission_classes([IsTeacherOrAdmin])
def create_activity(request):
    return Response({"message": "Created"})
```

### 6. `IsStudentOrTeacher`
Študenti ALEBO učitelia.

```python
@api_view(["GET"])
@permission_classes([IsStudentOrTeacher])
def get_activities(request):
    return Response({"activities": []})
```

### 7. `AllowAny`
Verejný endpoint (aj bez tokenu).

```python
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    return Response({"token": "..."})
```

---

## Frontend integrácia

### Axios (odporúčané)

```javascript
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000'
});

// Automaticky pridať token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Automaticky spracovať expirovaný token
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Použitie
api.get('/api/accounts/').then(res => console.log(res.data));
```

### Fetch

```javascript
const token = localStorage.getItem('token');

fetch('/api/endpoint/', {
    headers: { 'Authorization': `Bearer ${token}` }
})
.then(async response => {
    if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.href = '/login';
    }
    return response.json();
})
.then(data => console.log(data));
```

---

## Error kódy

### 401 Unauthorized (autentifikácia)

| Kód | Detail | Akcia |
|-----|--------|-------|
| `no_token` | Token nebol poskytnutý | Presmerovať na login |
| `token_expired` | Token expiroval (>8h) | Presmerovať na login |
| `invalid_token` | Token neplatný/poškodený | Presmerovať na login |
| `invalid_token_header` | Nesprávny formát | Opraviť na "Bearer token" |

### 403 Forbidden (autorizácia)

| Kód | Detail | Akcia |
|-----|--------|-------|
| `not_student` | Len pre študentov | Zobraziť error |
| `not_teacher` | Len pre učiteľov | Zobraziť error |
| `not_admin` | Len pre adminov | Zobraziť error |
| `insufficient_permissions` | Nedostatočné oprávnenia | Zobraziť error |

### Frontend spracovanie

```javascript
fetch('/api/endpoint/', {
    headers: { 'Authorization': `Bearer ${token}` }
})
.then(async response => {
    if (!response.ok) {
        const error = await response.json();
        
        // 401 - token problém
        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        
        // 403 - oprávnenia
        if (response.status === 403) {
            alert(`Nemáte oprávnenie: ${error.detail}`);
        }
        
        throw new Error(error.detail);
    }
    return response.json();
});
```

---

## Príklady endpointov

### Príklad 1: Študent vytvorí rezerváciu

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from accounts.permissions import IsStudent

@api_view(["POST"])
@permission_classes([IsStudent])
def create_reservation(request):
    """
    Vytvorenie rezervácie - LEN študenti.
    """
    activity_slot_id = request.data.get("activity_slot_id")
    note = request.data.get("note", "")
    
    try:
        activity_slot = ActivitySlot.objects.get(id=activity_slot_id)
    except ActivitySlot.DoesNotExist:
        return Response({
            "detail": "Activity slot not found.",
            "code": "slot_not_found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Kontrola duplikátu
    if Reservation.objects.filter(user=request.user, activity_slot=activity_slot).exists():
        return Response({
            "detail": "Already have reservation.",
            "code": "duplicate_reservation"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Vytvorenie
    reservation = Reservation.objects.create(
        user=request.user,
        activity_slot=activity_slot,
        note=note,
        status=Reservation.Status.PENDING
    )
    
    return Response({
        "detail": "Reservation created.",
        "reservation_id": reservation.id
    }, status=status.HTTP_201_CREATED)
```

**Test:**
```bash
# Študent - OK
curl -X POST http://127.0.0.1:8000/api/reservations/ \
  -H "Authorization: Bearer <STUDENT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"activity_slot_id": 1}'

# Učiteľ - FAIL (403 "not_student")
curl -X POST http://127.0.0.1:8000/api/reservations/ \
  -H "Authorization: Bearer <TEACHER_TOKEN>"
```

---

### Príklad 2: Učiteľ schváli rezerváciu

```python
from accounts.permissions import IsTeacher

@api_view(["PATCH"])
@permission_classes([IsTeacher])
def approve_reservation(request, reservation_id):
    """
    Schválenie rezervácie - LEN učitelia.
    """
    try:
        reservation = Reservation.objects.get(id=reservation_id)
    except Reservation.DoesNotExist:
        return Response({
            "detail": "Reservation not found."
        }, status=status.HTTP_404_NOT_FOUND)
    
    action = request.data.get("action")  # "approve" or "cancel"
    
    if action == "approve":
        reservation.status = Reservation.Status.APPROVED
    elif action == "cancel":
        reservation.status = Reservation.Status.CANCELLED
    else:
        return Response({
            "detail": "Invalid action."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    reservation.save()
    return Response({"detail": f"Reservation {action}d."})
```

**Test:**
```bash
# Učiteľ - OK
curl -X PATCH http://127.0.0.1:8000/api/reservations/1/approve/ \
  -H "Authorization: Bearer <TEACHER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"action": "approve"}'

# Študent - FAIL (403 "not_teacher")
curl -X PATCH http://127.0.0.1:8000/api/reservations/1/approve/ \
  -H "Authorization: Bearer <STUDENT_TOKEN>"
```

---

### Príklad 3: Admin vytvára aktivitu

```python
from accounts.permissions import IsAdmin

@api_view(["POST"])
@permission_classes([IsAdmin])
def create_activity(request):
    """
    Vytvorenie aktivity - LEN admini.
    """
    name = request.data.get("name")
    description = request.data.get("description")
    
    activity = Activity.objects.create(
        name=name,
        description=description,
        created_by=request.user
    )
    
    return Response({
        "detail": "Activity created.",
        "activity_id": activity.id
    }, status=status.HTTP_201_CREATED)
```

---

### Príklad 4: Komplexná logika (študent upraví svoju rezerváciu, učiteľ akúkoľvek)

```python
from accounts.permissions import IsAuthenticatedWithValidToken

@api_view(["PATCH"])
@permission_classes([IsAuthenticatedWithValidToken])
def update_reservation(request, reservation_id):
    """
    Úprava rezervácie:
    - Študenti: len SVOJE (note)
    - Učitelia: AKÚKOĽVEK (aj status)
    """
    try:
        reservation = Reservation.objects.get(id=reservation_id)
    except Reservation.DoesNotExist:
        return Response({
            "detail": "Not found."
        }, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    is_owner = reservation.user == user
    is_teacher = user.role and user.role.name.lower() == 'teacher'
    
    # Kontrola oprávnení
    if not (is_owner or is_teacher):
        return Response({
            "detail": "No permission.",
            "code": "insufficient_permissions"
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Note môže upraviť každý oprávnený
    note = request.data.get("note")
    if note:
        reservation.note = note
    
    # Status len učiteľ
    status_update = request.data.get("status")
    if status_update:
        if not is_teacher:
            return Response({
                "detail": "Only teachers can change status.",
                "code": "insufficient_permissions"
            }, status=status.HTTP_403_FORBIDDEN)
        reservation.status = status_update
    
    reservation.save()
    return Response({"detail": "Updated."})
```

---

## Testovanie

### Postman

1. **Login:**
   - Method: `POST`
   - URL: `http://127.0.0.1:8000/api/accounts/login/`
   - Headers: `Content-Type: application/json`
   - Body: `{"email":"horvath_a@katkinpark.sk","password":"T8f$Q2m!Lp7$"}`
   - → Skopíruj `token`

2. **Test bez tokenu:**
   - Method: `GET`
   - URL: `http://127.0.0.1:8000/api/accounts/`
   - → Expected: 401 `"no_token"`

3. **Test s tokenom:**
   - Method: `GET`
   - URL: `http://127.0.0.1:8000/api/accounts/`
   - Headers: `Authorization: Bearer <TOKEN>`
   - → Expected: 200 OK

---

## FAQ

**Q: Ako dlho je token platný?**  
A: Access: 8h, Refresh: 7d

**Q: Čo keď token expiruje?**  
A: Backend vráti 401 `"token_expired"` → frontend presmeruje na login

**Q: Môže študent pristúpiť k učiteľským datám?**  
A: Nie. Backend vráti 403 `"not_teacher"`

**Q: Kde uložiť token?**  
A: `localStorage` (web) alebo secure storage (mobile)

**Q: Musím token posielať pri každom requeste?**  
A: Áno, okrem login endpointu

---

## Konfigurácia

V `app/settings.py`:

```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'accounts.permissions.IsAuthenticatedWithValidToken',
    ),
}
```

---

## 🎉 Zhrnutie

✅ Každý endpoint validuje token (okrem login)  
✅ Token je dešifrovaný a overený backendom  
✅ Expirácia kontrolovaná pri každom requeste  
✅ Role-based permissions zabraňujú neautorizovanému prístupu  
✅ Jasné error messages pre frontend  

**Backend je bezpečný a pripravený!** 🔒
