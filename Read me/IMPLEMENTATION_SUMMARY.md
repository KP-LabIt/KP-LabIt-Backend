# Token Validation Implementation Summary

## ✅ Čo bolo implementované

### 1. **Custom Permission Classes** (`accounts/permissions.py`)

Vytvorené permission classes pre kompletnu validáciu tokenov:

- **`IsAuthenticatedWithValidToken`** - Základná validácia tokenu (5 krokov)
  - ✅ Kontrola prítomnosti tokenu
  - ✅ Validácia tokenu (bol vytvorený backendom)
  - ✅ Kontrola expirácie
  - ✅ Overenie používateľa
  - ✅ Validácia user_id

- **`IsStudent`** - Len pre študentov
- **`IsTeacher`** - Len pre učiteľov
- **`IsAdmin`** - Len pre administrátorov
- **`IsTeacherOrAdmin`** - Pre učiteľov a adminov
- **`IsStudentOrTeacher`** - Pre študentov a učiteľov

### 2. **JWT Configuration** (`app/settings.py`)

Nakonfigurovaný JWT systém:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),   # Token expiruje po 8h
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # Refresh po 7 dňoch
    'AUTH_HEADER_TYPES': ('Bearer',),              # Bearer token
}
```

Default permission pre všetky endpointy:
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'accounts.permissions.IsAuthenticatedWithValidToken',
    ),
}
```

### 3. **Updated Endpoints**

#### `accounts/views.py`:
- ✅ **`login`** - Verejný endpoint (AllowAny) - vráti token
- ✅ **`change_password`** - Vyžaduje IsAuthenticatedWithValidToken
- ✅ **`get_init`** - Vyžaduje IsAuthenticatedWithValidToken

#### `api/views.py`:
- ✅ **`get_init`** - Vyžaduje IsAuthenticatedWithValidToken

### 4. **Documentation**

- ✅ **`TOKEN_VALIDATION.md`** - Kompletná dokumentácia
  - Ako systém funguje
  - Príklady pre frontend (Fetch, Axios, React)
  - Error kódy
  - Testing príklady
  - Security best practices

- ✅ **`EXAMPLE_ENDPOINTS.py`** - Príklady použitia
  - 7 rôznych príkladov endpointov
  - Študent-only, Teacher-only, Admin-only
  - Komplexné permission logiky

- ✅ **`README.md`** - Aktualizovaný README
  - Informácie o token validation
  - Základné použitie
  - Link na kompletnú dokumentáciu

## 🔐 Ako to funguje

### Token Flow:

```
1. POST /api/accounts/login/
   → Backend vygeneruje JWT token
   → Vráti: { token, refresh_token, user }

2. Frontend uloží token

3. GET /api/endpoint/
   Authorization: Bearer <token>
   
4. Backend validuje token:
   ✓ Token je prítomný?
   ✓ Token je validný? (podpis)
   ✓ Token nie je expirovaný?
   ✓ User_id sa zhoduje?
   ✓ Používateľ má správnu rolu?
   
5a. Ak OK → Pokračuje spracovanie
5b. Ak NOK → Vráti 401/403 error

6. Frontend pri 401 "token_expired"
   → Presmeruje na login
```

### Validation Steps (5 krokov):

```python
# Krok 1: Token je prítomný
if not auth_header.startswith('Bearer '):
    raise AuthenticationFailed("no_token")

# Krok 2: Token je validný (bol vytvorený backendom)
token = AccessToken(token_string)  # Validuje podpis

# Krok 3: Token nie je expirovaný
if datetime.now() > exp_datetime:
    raise AuthenticationFailed("token_expired")

# Krok 4: User_id sa zhoduje
if token_user_id != request.user.id:
    raise AuthenticationFailed("token_user_mismatch")

# Krok 5: Rola je správna (role-based permissions)
if request.user.role.name != 'student':
    raise PermissionDenied("not_student")
```

## 📝 Error Codes

| Kód | Význam | Status | Akcia |
|-----|--------|--------|-------|
| `no_token` | Token nebol poskytnutý | 401 | Presmerovať na login |
| `token_expired` | Token expiroval | 401 | **Presmerovať na login** |
| `invalid_token` | Token je neplatný | 401 | Presmerovať na login |
| `invalid_token_header` | Nesprávny formát | 401 | Opraviť formát |
| `not_student` | Nie je študent | 403 | Zobraziť error |
| `not_teacher` | Nie je učiteľ | 403 | Zobraziť error |
| `not_admin` | Nie je admin | 403 | Zobraziť error |
| `insufficient_permissions` | Nedostatočné oprávnenia | 403 | Zobraziť error |

## 🎯 Príklady použitia

### Endpoint pre všetkých (autentifikovaných)

```python
@api_view(["GET"])
@permission_classes([IsAuthenticatedWithValidToken])
def my_endpoint(request):
    # Token je validovaný
    user = request.user
    return Response({"message": "Success"})
```

### Endpoint len pre študentov

```python
@api_view(["POST"])
@permission_classes([IsStudent])
def student_only(request):
    # Len študenti môžu pristúpiť
    return Response({"message": "Student action"})
```

### Endpoint len pre učiteľov

```python
@api_view(["GET"])
@permission_classes([IsTeacher])
def teacher_only(request):
    # Len učitelia môžu pristúpiť
    return Response({"data": "Teacher data"})
```

### Verejný endpoint (bez tokenu)

```python
from rest_framework.permissions import AllowAny

@api_view(["POST"])
@permission_classes([AllowAny])
def public_endpoint(request):
    # Prístupné pre každého
    return Response({"message": "Public"})
```

## 🌐 Frontend Integration

### JavaScript (Fetch)

```javascript
const token = localStorage.getItem('token');

fetch('/api/endpoint/', {
    headers: {
        'Authorization': `Bearer ${token}`
    }
})
.then(response => {
    if (response.status === 401) {
        // Token expirovaný
        localStorage.removeItem('token');
        window.location.href = '/login';
    }
    return response.json();
})
.then(data => console.log(data));
```

### JavaScript (Axios)

```javascript
import axios from 'axios';

const api = axios.create({ baseURL: 'http://localhost:8000' });

// Automaticky pridať token
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle expirovaný token
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

## 🧪 Testing

### Test s curl:

```bash
# 1. Login
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"student@katkinpark.sk","password":"heslo123"}'

# Response: {"token": "eyJ0...", ...}

# 2. Use token
curl -X GET http://localhost:8000/api/endpoint/ \
  -H "Authorization: Bearer eyJ0..."
```

### Test bez tokenu (malo by zlyhať):

```bash
curl -X GET http://localhost:8000/api/endpoint/
# Expected: 401 Unauthorized
```

## 📋 Checklist pre nový endpoint

Pri vytváraní nového endpointu:

- [ ] Import potrebných permission classes
- [ ] Pridaj `@permission_classes([...])`
- [ ] Vyber správnu permission class:
  - `IsAuthenticatedWithValidToken` - všetci
  - `IsStudent` - len študenti
  - `IsTeacher` - len učitelia
  - `IsAdmin` - len admini
  - `IsTeacherOrAdmin` - učitelia a admini
  - `IsStudentOrTeacher` - študenti a učitelia
  - `AllowAny` - verejný endpoint
- [ ] Otestuj bez tokenu (malo by zlyhať s 401)
- [ ] Otestuj s nesprávnou rolou (malo by zlyhať s 403)
- [ ] Otestuj so správnou rolou (malo by uspieť)

## 🔒 Security Features

### ✅ Implementované:

1. **Token je vždy validovaný** na každom endpointe
2. **Expirácia je kontrolovaná** - expirované tokeny sú odmietnuté
3. **Role-based access control** - študent nemôže vidieť učiteľské dáta
4. **Jasné error messages** s kódmi pre frontend
5. **Default permission** - všetky endpointy vyžadujú token
6. **Explicit public endpoints** - musí byť explicitne označené ako AllowAny

### ⚡ Best Practices:

- Token sa **nikdy** nedôveruje len z frontendu
- Backend **vždy** dešifruje a validuje token
- Expirované tokeny sú **okamžite** odmietnuté
- Role sú brané len z **validovaného tokenu**
- Citlivé dáta **nie sú** v tokene (len id, email, role, meno)

## 📚 Súbory

Vytvorené/upravené súbory:

1. ✅ `accounts/permissions.py` - Permission classes
2. ✅ `app/settings.py` - JWT configuration
3. ✅ `accounts/views.py` - Updated endpoints
4. ✅ `api/views.py` - Updated endpoints
5. ✅ `TOKEN_VALIDATION.md` - Kompletná dokumentácia
6. ✅ `EXAMPLE_ENDPOINTS.py` - Príklady endpointov
7. ✅ `README.md` - Aktualizovaný README
8. ✅ `IMPLEMENTATION_SUMMARY.md` - Tento súbor

## 🎉 Summary

Systém je **kompletne implementovaný** a pripravený na použitie:

✅ **Každý endpoint validuje token** (okrem login)  
✅ **Token je dešifrovaný a overený** že bol vytvorený backendom  
✅ **Expirácia je kontrolovaná** pri každom requeste  
✅ **Role-based permissions** zabraňujú neautorizovanému prístupu  
✅ **Jasné error messages** pre frontend  
✅ **Kompletná dokumentácia** s príkladmi  

