# KP-LabIt-Backend

## na správne inicializovanie backendu:

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

3. pripojenie do db a nastavenie SECRET_KEY:

- v priečinku app si vytvore .env súbor, kde vložíte db údaje, ktoré som posielal.
- ako dalej sa odporuca vygenerovat vlastny django SECRET_KEY, aby sa predislo warningom typu “Session data corrupted” (Produkčný server bude používať jeden stály SECRET_KEY, ktorý sa lokálne nepoužíva a nikdy sa nezdieľa.).
- na vygenerovanie SECRET_KEY:

  ```bash
      python manage.py shell
      from django.core.management.utils import get_random_secret_key
      get_random_secret_key()
  ```

- funkcia vam vrati kluc, ktory si potom treba pridat do .env súboru takto -> SECRET_KEY_SETTINGS=vygenerovany_kluc

4. spustenie django appky:

Windows:

```bash
python manage.py runserver
```

Mac:

```bash
python3 manage.py runserver
```
