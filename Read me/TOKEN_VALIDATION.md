# Token Validation System - Dokumentácia

## Prehľad (Overview)

Tento backend implementuje **kompletný systém validácie JWT tokenov** pre všetky endpointy. Každý request (okrem login) musí obsahovať platný JWT token, ktorý backend dešifruje, validuje a kontroluje expir áciu.

## Ako to funguje

### Proces validácie tokenu

Každý endpoint (okrem login) vykonáva **5-stupňovú validáciu**:

1. **Token je prítomný** - Backend kontroluje, či je token v Authorization hlavičke
2. **Token je validný** - Backend overuje, či token bol vytvorený týmto backendom (validný podpis)
3. **Token nie je expirovaný** - Backend dešifruje token a kontroluje expiration timestamp
4. **Používateľ je autentifikovaný** - Backend overuje, či token patrí existujúcemu používateľovi
5. **Používateľ má správnu rolu** - Backend kontroluje, či má používateľ oprávnenie pristúpiť k endpointu

### Token Lifecycle

```
1. Login → Backend vygeneruje token → Vráti token frontendovu
2. Frontend uloží token
3. Frontend posiela token s každým requestom
4. Backend validuje token pri každom requeste
5. Ak token expiruje → Backend vráti "token_expired" error
6. Frontend požiada používateľa o nové prihlásenie
```

## Požiadavky na Frontend

Frontend **MUSÍ**:

✅ Posielať token v HTTP hlavičke s každým requestom (okrem login)  
✅ Použiť formát: `Authorization: Bearer <token>`  
✅ Spracovať 401 error s kódom "token_expired"  
✅ Presmerovať používateľa na login pri expirácii tokenu  
✅ Uložiť token bezpečne (localStorage / secure storage)

## Endpointy

### Login (Verejný - bez tokenu)

**Endpoint:** `POST /api/accounts/login/`

**Request:**
```json
{
    "email": "student@katkinpark.sk",
    "password": "heslo123"
}
```

**Response:**
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "must_change_password": true,
    "user": {
        "id": 1,
        "email": "student@katkinpark.sk",
        "firstName": "Ján",
        "lastName": "Novák",
        "role": "student"
    }
}
```

### Ostatné endpointy (Vyžadujú token)

Všetky ostatné endpointy vyžadujú:

```http
GET /api/endpoint/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Permission Classes

### `IsAuthenticatedWithValidToken`
- Používa sa pre všetkých autentifikovaných používateľov
- Validuje token, ale nekontroluje rolu

```python
@api_view(["GET"])
@permission_classes([IsAuthenticatedWithValidToken])
def my_endpoint(request):
    # Prístupné pre všetkých s platným tokenom
    return Response({"message": "Success"})
```

### `IsStudent`
- Len pre študentov
- Učitelia dostanú 403 Forbidden error

```python
@api_view(["POST"])
@permission_classes([IsStudent])
def create_reservation(request):
    # Len študenti môžu vytvárať rezervácie
    return Response({"message": "Reservation created"})
```

### `IsTeacher`
- Len pre učiteľov
- Študenti dostanú 403 Forbidden error

```python
@api_view(["GET"])
@permission_classes([IsTeacher])
def get_all_reservations(request):
    # Len učitelia môžu vidieť všetky rezervácie
    return Response({"reservations": []})
```

### `IsTeacherOrAdmin`
- Pre učiteľov a administrátorov
- Študenti dostanú 403 Forbidden error

```python
@api_view(["POST"])
@permission_classes([IsTeacherOrAdmin])
def approve_reservation(request):
    # Len učitelia/admini môžu schvaľovať rezervácie
    return Response({"message": "Approved"})
```

### `IsStudentOrTeacher`
- Pre študentov a učiteľov
- Ostatné role dostanú 403 Forbidden error

```python
@api_view(["GET"])
@permission_classes([IsStudentOrTeacher])
def get_activities(request):
    # Študenti a učitelia môžu vidieť aktivity
    return Response({"activities": []})
```

## Error Responses

### Token chýba
```json
{
    "detail": "Authentication credentials were not provided.",
    "code": "no_token"
}
```
**Status:** 401 Unauthorized

### Token je expirovaný
```json
{
    "detail": "Token has expired. Please login again.",
    "code": "token_expired"
}
```
**Status:** 401 Unauthorized  
**Frontend akcia:** Presmerovať na login

### Token je neplatný
```json
{
    "detail": "Token is invalid: <detail>",
    "code": "invalid_token"
}
```
**Status:** 401 Unauthorized

### Nesprávny formát tokenu
```json
{
    "detail": "Invalid token header. Token must be provided as 'Bearer <token>'.",
    "code": "invalid_token_header"
}
```
**Status:** 401 Unauthorized

### Nedostatočné oprávnenia (nesprávna rola)
```json
{
    "detail": "This endpoint is only accessible to students.",
    "code": "not_student"
}
```
**Status:** 403 Forbidden

**Príklady kódov:**
- `not_student` - Endpoint len pre študentov
- `not_teacher` - Endpoint len pre učiteľov
- `not_admin` - Endpoint len pre adminov
- `insufficient_permissions` - Nedostatočné oprávnenia
- `no_role` - Používateľ nemá priradenú rolu

## Frontend Integration

### JavaScript (Fetch API)

```javascript
// Uložiť token po logine
const loginResponse = await fetch('/api/accounts/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'student@katkinpark.sk',
        password: 'heslo123'
    })
});

const loginData = await loginResponse.json();
localStorage.setItem('token', loginData.token);

// Použiť token v requestoch
const token = localStorage.getItem('token');

fetch('/api/endpoint/', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    }
})
.then(response => {
    if (response.status === 401) {
        // Token expirovaný - presmerovať na login
        localStorage.removeItem('token');
        window.location.href = '/login';
    }
    return response.json();
})
.then(data => console.log(data))
.catch(error => console.error(error));
```

### JavaScript (Axios)

```javascript
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
});

// Automaticky pridať token ku každému requestu
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Automaticky spracovať expirované tokeny
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401 && 
            error.response?.data?.code === 'token_expired') {
            // Token expirovaný
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Použitie
api.get('/api/endpoint/')
    .then(response => console.log(response.data))
    .catch(error => console.error(error));
```

### React Example

```javascript
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function MyComponent() {
    const [data, setData] = useState(null);
    const token = localStorage.getItem('token');

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('/api/endpoint/', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                setData(response.data);
            } catch (error) {
                if (error.response?.status === 401) {
                    // Token expirovaný
                    localStorage.removeItem('token');
                    window.location.href = '/login';
                }
            }
        };

        fetchData();
    }, [token]);

    return <div>{data && JSON.stringify(data)}</div>;
}
```

## Backend Configuration

### Token Lifetime

- **Access Token:** Expiruje po **8 hodinách**
- **Refresh Token:** Expiruje po **7 dňoch**

Nastavené v `app/settings.py`:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

### Default Permission

Všetky endpointy majú predvolene nastavenú `IsAuthenticatedWithValidToken`:

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'accounts.permissions.IsAuthenticatedWithValidToken',
    ),
}
```

**Výnimky (verejné endpointy)** musia explicitne použiť:

```python
from rest_framework.permissions import AllowAny

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    # Verejný endpoint
    pass
```

## Testovanie

### Test s platným tokenom (curl)

```bash
# 1. Login
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"student@katkinpark.sk","password":"heslo123"}'

# Response: {"token": "eyJ0...", ...}

# 2. Použiť token
curl -X GET http://localhost:8000/api/endpoint/ \
  -H "Authorization: Bearer eyJ0..."
```

### Test bez tokenu (malo by zlyhať)

```bash
curl -X GET http://localhost:8000/api/endpoint/
# Expected: 401 Unauthorized
```

### Test s expirovaným tokenom

```bash
curl -X GET http://localhost:8000/api/endpoint/ \
  -H "Authorization: Bearer <expired_token>"
# Expected: 401 Unauthorized s kódom "token_expired"
```

### Test role-based permissions

```bash
# Študent sa pokúša pristúpiť k teacher-only endpointu
curl -X GET http://localhost:8000/api/teacher-endpoint/ \
  -H "Authorization: Bearer <student_token>"
# Expected: 403 Forbidden s kódom "not_teacher"
```

## Príklady použitia

### Endpoint pre všetkých autentifikovaných

```python
@api_view(["GET"])
@permission_classes([IsAuthenticatedWithValidToken])
def get_user_profile(request):
    """Každý s platným tokenom môže pristúpiť"""
    user = request.user
    return Response({
        "id": user.id,
        "email": user.email,
        "role": user.role.name if user.role else None
    })
```

### Endpoint len pre študentov

```python
@api_view(["POST"])
@permission_classes([IsStudent])
def create_reservation(request):
    """Len študenti môžu vytvárať rezervácie"""
    # Študent môže rezervovať
    # Učiteľ dostane 403 Forbidden
    return Response({"message": "Reservation created"})
```

### Endpoint len pre učiteľov

```python
@api_view(["GET"])
@permission_classes([IsTeacher])
def get_all_reservations(request):
    """Len učitelia môžu vidieť všetky rezervácie"""
    # Učiteľ vidí všetky rezervácie
    # Študent dostane 403 Forbidden
    reservations = Reservation.objects.all()
    return Response({"reservations": []})
```

### Komplexná logika s rolami

```python
@api_view(["PATCH"])
@permission_classes([IsAuthenticatedWithValidToken])
def update_reservation(request, reservation_id):
    """
    Študenti môžu editovať svoje vlastné rezervácie.
    Učitelia môžu editovať akékoľvek rezervácie.
    """
    reservation = Reservation.objects.get(id=reservation_id)
    user = request.user
    
    # Vlastná logika
    is_owner = reservation.user == user
    is_teacher = user.role and user.role.name.lower() == 'teacher'
    
    if not (is_owner or is_teacher):
        return Response({
            "detail": "You cannot update this reservation.",
            "code": "insufficient_permissions"
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Pokračovať v editácii
    return Response({"message": "Updated"})
```

## Security Best Practices

### ✅ DO (Správne praktiky)

1. **Vždy validovať token na backende**
   - Nikdy neveriť frontendovým údajom
   - Vždy dešifrovať a validovať token

2. **Kontrolovať expiráciu**
   - Okamžite odmietnuť expirované tokeny
   - Vrátiť jasný error kód

3. **Používať role-based access control**
   - Študent nemôže pristúpiť k učiteľským dátam
   - Každá rola má špecifické oprávnenia

4. **Ukladať tokeny bezpečne**
   - Web: localStorage (ideálne httpOnly cookies)
   - Mobile: Secure storage (Keychain/Keystore)

5. **Logovať neautorizované prístupy**
   - Monitorovať podozrivé aktivity
   - Blokovať opakované neplatné pokusy

### ❌ DON'T (Nesprávne praktiky)

1. **Nikdy nekontrolovať token len na frontende**
   - Backend MUSÍ vždy validovať

2. **Nikdy nepovoliť prístup s expirovaným tokenom**
   - Vždy vrátiť error

3. **Nikdy nedôverovať role z frontendu**
   - Rolu vždy brať z validovaného tokenu

4. **Nikdy neukladať citlivé dáta v tokene**
   - Token je dekódovateľný (base64)
   - Heslo NIKDY nedávať do tokenu

## Summary

### Čo systém robí:

✅ **Každý endpoint validuje token** (okrem login)  
✅ **Token je dešifrovaný a overený** že bol vytvorený backendom  
✅ **Expirácia je kontrolovaná** pri každom requeste  
✅ **Role-based permissions** zabraňujú neautorizovanému prístupu  
✅ **Jasné error messages** s kódmi pre frontend  
✅ **Bezpečná autentifikácia** so štandardným JWT

### Workflow:

1. Používateľ sa prihlási → Dostane token
2. Frontend posiela token s každým requestom
3. Backend validuje token (prítomnosť, validita, expirácia, rola)
4. Ak token OK → Pokračuje spracovanie requestu
5. Ak token BAD → Vráti 401/403 error
6. Frontend spracuje error a presmeruje na login

Systém je teraz **plne zabezpečený** a pripravený na produkčné použitie.
