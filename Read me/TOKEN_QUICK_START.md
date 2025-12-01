## 🔐 Token Validation System

Tento backend má **kompletný systém validácie JWT tokenov** pre všetky endpointy.

### Ako to funguje:

✅ **Každý endpoint vyžaduje validný JWT token** (okrem login)  
✅ **Token je dešifrovaný a validovaný** - backend overuje, že token bol vytvorený backendom  
✅ **Expirácia je kontrolovaná** - expirované tokeny sú okamžite odmietnuté  
✅ **Role-based permissions** - študent nemôže pristúpiť k učiteľským endpointom  
✅ **Bezpečná autentifikácia** - štandardný JWT s kompletnou validáciou

### Používanie tokenov:

**1. Login (získať token):**

```bash
POST /api/accounts/login/
Content-Type: application/json

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

**2. Použiť token v requestoch:**

```bash
GET /api/endpoint/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Token Lifetime:

- **Access Token:** Expiruje po **8 hodinách**
- **Refresh Token:** Expiruje po **7 dňoch**

### Error Responses:

- `401 Unauthorized` + `"token_expired"` - Token expiroval, presmerovať na login
- `401 Unauthorized` + `"no_token"` - Token nebol poskytnutý
- `401 Unauthorized` + `"invalid_token"` - Token je neplatný
- `403 Forbidden` + `"not_student"` - Nedostatočné oprávnenia (nesprávna rola)

### Viac informácií:

📖 **[TOKEN_VALIDATION.md](TOKEN_VALIDATION.md)** - Kompletná dokumentácia s príkladmi pre frontend  
📖 **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Technické zhrnutie implementácie  
📖 **[EXAMPLE_ENDPOINTS.py](EXAMPLE_ENDPOINTS.py)** - Príklady kódu pre rôzne endpointy
