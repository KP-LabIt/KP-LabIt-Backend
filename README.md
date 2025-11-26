# KP-LabIt-Backend

na správne inicializovanie backendu:

1. vytvoriť lokálny venv súbor:

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Mac:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. nainštaluj requirements.txt:

```bash
pip install -r requirements.txt
```

3. pripojenie do db:

v priečinku app si vytvore .env súbor, kde vložíte db údaje, ktoré som posielal.

4. spustenie django appky:

Windows:

```bash
python manage.py runserver
```

Mac:

```bash
python3 manage.py runserver
```
