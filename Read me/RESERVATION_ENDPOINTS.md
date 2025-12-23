# API Dokumentácia - Rezervácie

Tento dokument popisuje endpointy pre prácu s rezerváciami používateľa. Rozlišuje sa správanie pre **študentov** a **učiteľov**.

---

## Endpointy

### 1. GET `/api/reservations/`

Získanie zoznamu rezervácií pre prihláseného používateľa.

#### Správanie podľa role:

- **Študent**: Získa všetky svoje budúce rezervácie (aktivita ešte neprebehla)
- **Učiteľ**: Získa všetky budúce rezervácie, kde je priradený k aktivite slotu

#### Autentifikácia:

- **Požadovaná**: Áno
- **Permissions**: `IsAuthenticatedWithValidToken`

#### Filtrovanie:

Vrátia sa iba rezervácie, kde `activity_slot.end_date >= now` (ešte neprebehli)

#### Response:

**Status**: `200 OK`

**Body** (JSON Array):

```json
[
  {
    "id": 10,
    "user": {
      "id": 144,
      "email": "petric_r@katkinpark.sk",
      "first_name": "",
      "last_name": "",
      "role": "student"
    },
    "activity_slot": {
      "id": 2,
      "start_date": "2025-12-22T17:30:59Z",
      "end_date": "2025-12-22T17:40:00Z",
      "activity": {
        "id": 1,
        "name": "PS5",
        "description": "Zahrajte si najnovšie hry na našom PS5.",
        "capacity": 2,
        "available_hours": "7:30-16:00",
        "color": "#778899",
        "category": "zábava",
        "room": "28",
        "role": 3
      },
      "teacher": null
    },
    "note": "Poznámka k rezervácii",
    "created_at": "2025-12-22T19:19:46.102249Z",
    "status": null,
    "status_label": null
  }
]
```

#### Poznámka:

Tento endpoint iba číta dáta, nekontroluje kapacitu ani duplikáty.

---

### 2. PATCH `/api/reservations/change_status/<reservation_id>/`

Zmena statusu rezervácie učiteľom.

#### Účel:

Umožní učiteľovi, ktorý je priradený k danému slotu, zmeniť status rezervácie.

#### Autentifikácia:

- **Požadovaná**: Áno
- **Permissions**: `IsTeacher`

#### URL Parameters:

- `reservation_id` (integer) - ID rezervácie

#### Request Body:

```json
{
  "status": "approved"
}
```

**Validné statusy:**

- `"pending"`
- `"cancelled"`
- `"approved"`

#### Response:

**Status**: `200 OK`

**Body**:

```json
{
  "detail": "Status rezervácie bol úspešne zmenený."
}
```

#### Chybové odpovede:

**Status**: `404 Not Found`

```json
{
  "detail": "Rezervácia neexistuje alebo učiteľ nemá oprávnenie."
}
```

**Status**: `400 Bad Request`

```json
{
  "detail": "Neplatný status."
}
```

---

### 3. DELETE `/api/reservations/delete/<reservation_id>/`

Vymazanie konkrétnej rezervácie.

#### Účel:

Vymaže konkrétnu rezerváciu pre aktuálne prihláseného používateľa.

#### Autentifikácia:

- **Požadovaná**: Áno
- **Permissions**: `IsAuthenticatedWithValidToken`

#### URL Parameters:

- `reservation_id` (integer) - ID rezervácie na zmazanie

#### Response:

**Status**: `200 OK`

**Body**:

```json
{
  "detail": "Rezervácia bola úspešne zmazaná."
}
```

#### Chybové odpovede:

**Status**: `404 Not Found`

```json
{
  "detail": "Rezervácia neexistuje alebo patrí inému používateľovi."
}
```

---

## Príklady použitia

### Študent

#### Získať všetky svoje rezervácie:

```http
GET /api/reservations/
Authorization: Bearer <JWT_TOKEN>
```

#### Vymazať svoju rezerváciu:

```http
DELETE /api/reservations/delete/5/
Authorization: Bearer <JWT_TOKEN>
```

---

### Učiteľ

#### Získať všetky rezervácie pre svoje activity sloty:

```http
GET /api/reservations/
Authorization: Bearer <JWT_TOKEN>
```

#### Zmeniť status rezervácie:

```http
PATCH /api/reservations/change_status/10/
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "status": "approved"
}
```

---

## Dôležité poznámky

1. **Študent** vidí iba svoje budúce rezervácie
2. **Učiteľ** vidí iba rezervácie, ktoré patria k jeho `activity_slot`om a ktoré ešte neprebehli
3. Backend zabezpečuje validáciu a oprávnenia, takže neoprávnené prístupy nie sú možné, aj keď sa frontendové údaje zmenia manuálne
4. Všetky časové údaje sú v UTC formáte (ISO 8601)
5. JWT token je potrebné posielať v hlavičke `Authorization` ako `Bearer <token>`

---

## Bezpečnosť

- Všetky endpointy vyžadujú platnú JWT autentifikáciu
- Kontrola oprávnení sa vykonáva na úrovni backendu
- Študenti nemôžu pristupovať k rezerváciám iných študentov
- Učitelia môžu meniť status iba pre rezervácie svojich activity slotov
