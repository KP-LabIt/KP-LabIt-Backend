Tento dokument popisuje endpointy pre prácu s rezerváciami používateľa.

---

## 1. GET `/api/reservations/`

- Účel: Získa všetky rezervácie pre aktuálne prihláseného používateľa.
- Permissions: Vyžaduje autentifikáciu (`IsAuthenticatedWithValidToken`).
- Response JSON obsahuje pole objektov, kde každý objekt má nasledovnú štruktúru:

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
    "note": "tfutfuuzfuz",
    "created_at": "2025-12-22T19:19:46.102249Z",
    "status": null,
    "status_label": null
  }
]
```

- Poznámka: Tento endpoint iba číta dáta, **nekontroluje kapacitu ani duplikáty**.

---

## 2. DELETE `/api/reservations/delete/<reservation_id>/`

- Účel: Vymaže konkrétnu rezerváciu používateľa.
- Permissions: Vyžaduje autentifikáciu (`IsAuthenticatedWithValidToken`).
- Overenie:
  - Rezervácia musí patriť aktuálnemu používateľovi.
- Request: `DELETE /api/reservations/delete/5/` (kde `5` je ID rezervácie)
- Response JSON pri úspechu:

```json
{
  "detail": "Rezervácia bola úspešne zmazaná."
}
```

- Ak rezervácia neexistuje alebo patrí inému používateľovi → 404 Not Found
