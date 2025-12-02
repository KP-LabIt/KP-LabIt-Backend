# 🔐 JWT Token Validation - Dokumentácia

## Prehľad

Backend má **kompletný systém validácie JWT tokenov** s 5-stupňovou validáciou a role-based access control.

- **Token expirácia:** 8h (access), 7d (refresh)
- **Validácia:** Token prítomný → Validný podpis → Nie expirovaný → User_id OK → Správna rola
- **Ochrana:** Všetky endpointy okrem login

## Rýchly štart

### 1. Login
```javascript
const res = await fetch('/api/accounts/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'user@katkinpark.sk', password: 'pass' })
});
const { token } = await res.json();
localStorage.setItem('token', token);
```

### 2. Použiť token
```javascript
fetch('/api/endpoint/', {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
});
```

## Permission Classes

```python
from accounts.permissions import IsStudent, IsTeacher, IsAdmin, IsTeacherOrAdmin
from rest_framework.permissions import AllowAny

# Len študenti
@permission_classes([IsStudent])

# Len učitelia
@permission_classes([IsTeacher])

# Len admini
@permission_classes([IsAdmin])

# Učitelia ALEBO admini
@permission_classes([IsTeacherOrAdmin])

# Verejný endpoint (login)
@permission_classes([AllowAny])
```

## Frontend integrácia (Axios)

```javascript
import axios from 'axios';

const api = axios.create({ baseURL: 'http://127.0.0.1:8000' });

// Auto-pridať token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

// Auto-logout pri 401
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
```

## Error kódy

| Status | Kód | Akcia |
|--------|-----|-------|
| 401 | `no_token` / `token_expired` / `invalid_token` | Presmerovať na login |
| 403 | `not_student` / `not_teacher` / `not_admin` | Zobraziť chybu |

## Príklady endpointov

### Študent vytvorí rezerváciu
```python
from accounts.permissions import IsStudent

@api_view(["POST"])
@permission_classes([IsStudent])
def create_reservation(request):
    reservation = Reservation.objects.create(
        user=request.user,
        activity_slot_id=request.data.get("activity_slot_id")
    )
    return Response({"id": reservation.id}, status=201)
```

### Učiteľ schváli rezerváciu
```python
from accounts.permissions import IsTeacher

@api_view(["PATCH"])
@permission_classes([IsTeacher])
def approve_reservation(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    reservation.status = "APPROVED"
    reservation.save()
    return Response({"detail": "Approved"})
```

### Komplexná logika (vlastník alebo učiteľ)
```python
@permission_classes([IsAuthenticatedWithValidToken])
def update_reservation(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    is_owner = reservation.user == request.user
    is_teacher = request.user.role.name == 'teacher'
    
    if not (is_owner or is_teacher):
        return Response({"detail": "No permission"}, status=403)
    
    # Ďalšia logika...
```

## FAQ

- **Ako dlho platí token?** Access: 8h, Refresh: 7d
- **Kde uložiť token?** `localStorage` (web) alebo secure storage (mobile)
- **Token pri každom requeste?** Áno (okrem login)
- **Študent pristúpi k admin datám?** Nie → 403 `"not_admin"`

## Konfigurácia (`app/settings.py`)

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'accounts.permissions.IsAuthenticatedWithValidToken',
    ),
}
```

---

**✅ Backend je bezpečný s kompletnou JWT validáciou!** 🔒
