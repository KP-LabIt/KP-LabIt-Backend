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
- na vygenerovanie SECRET_KEY (POZOR, treba byt v django shell pomocou commandu -> python manage.py shell):

  ```bash
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

## CI/CD (GitHub Actions)

- **CI** (`.github/workflows/ci.yml`): on every push/PR to `main`, `master`, or `develop` — install deps, `manage.py check`, `migrate` on SQLite, `test`.
- **CD** (`.github/workflows/cd.yml`): on push to `main`/`master` or tag `v*` — build Docker image and push to **GitHub Container Registry** (`ghcr.io/<org>/<repo>`).

**Run the container** (set real env vars):

```bash
docker run -p 8000:8000 \
  -e SECRET_KEY_SETTINGS=... \
  -e DATABASE_URL=postgresql://... \
  ghcr.io/kp-labit/kp-labit-backend:latest
```

Then run migrations once (empty DB: use `--skip-checks` the first time):

```bash
docker run --rm -e SECRET_KEY_SETTINGS=... -e DATABASE_URL=... IMAGE \
  python manage.py migrate --noinput --skip-checks
```

See `Read me/CI_CD_COMPATIBILITY.md` for details.

Copy `.env.example` to `.env` locally; never commit `.env`.
