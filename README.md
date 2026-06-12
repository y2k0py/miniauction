# MiniAukcje

Uproszczona platforma aukcyjna zbudowana w ramach projektu z przedmiotu Inżynieria Oprogramowania.

## Wymagania

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Uruchomienie

```bash
# Instalacja zależności
uv sync

# Migracje i dane startowe
uv run python manage.py migrate
uv run python manage.py seed_categories

# Opcjonalnie: konto administratora
uv run python manage.py createsuperuser

# Opcjonalnie: dane demonstracyjne (sprzedawca1 / kupujacy1, hasło: demo12345)
uv run python manage.py seed_demo

# Serwer deweloperski
uv run python manage.py runserver
```

Aplikacja dostępna pod adresem: http://127.0.0.1:8000/

## Komendy pomocnicze

```bash
# Zakończenie wygasłych aukcji i wyznaczenie zwycięzców
uv run python manage.py end_auctions

# Uruchomienie testów
uv run python manage.py test

# Generowanie dokumentacji DOCX
uv run python scripts/generate_docx.py
```

## Struktura projektu

- `accounts/` — rejestracja, logowanie, profil użytkownika
- `auctions/` — aukcje, licytacja, kategorie, watchlist
- `notifications/` — powiadomienia e-mail
- `docs/` — dokumentacja projektowa (PL), diagramy UML, zrzuty ekranu
- `docs/dokumentacja-projektu.docx` — wersja DOCX do oddania na MS Teams

## Konfiguracja e-mail (opcjonalna)

Skopiuj `.env.example` do `.env` i ustaw zmienne SMTP. Domyślnie e-maile wyświetlają się w konsoli.
