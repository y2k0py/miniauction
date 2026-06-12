# MiniAukcje — dokumentacja projektu

**Przedmiot:** Inżynieria Oprogramowania  
**Temat:** MiniAukcje — uproszczona platforma aukcyjna  
**Wykonawca:** projekt indywidualny  
**Technologie:** Python, uv, Django, SQLite  
**Data:** czerwiec 2026

---

## 1. Opis projektu

MiniAukcje to prosta platforma aukcyjna. Użytkownik wystawia przedmiot, inni licytują, a po czasie system wybiera zwycięzcę. Bez płatności i wysyłki.

### Funkcje

1. Rejestracja i logowanie
2. Tworzenie aukcji
3. Licytacja
4. Kategorie i wyszukiwanie
5. Lista obserwowanych
6. Powiadomienia e-mail
7. Zakończenie aukcji
8. Usuwanie aukcji (bez ofert)

### Moduły

- `accounts` — konta użytkowników
- `auctions` — aukcje i licytacja
- `notifications` — e-mail

---

## 2. Plan i zasoby

| Tydzień | Zakres | Czas |
|---------|--------|------|
| 1 | Setup, logowanie | 10 h |
| 2 | Aukcje, licytacja | 12 h |
| 3 | Watchlist, maile, testy | 10 h |
| 4 | Dokumentacja, prezentacja | 13 h |

Wykonawca: 1 osoba. Sprzęt: laptop. Baza: SQLite.

---

## 3. Ryzyka i koszty

- Opóźnienie → praca w małych etapach
- Błąd licytacji → testy automatyczne
- Problemy z e-mail → wysyłka w konsoli

**Koszt:** ok. 2500 PLN (50 h × 50 PLN/h)

---

## 4. Przypadki użycia

- **Gość** — przegląda aukcje
- **Użytkownik** — licytuje, obserwuje
- **Sprzedawca** — dodaje i usuwa aukcje
- **System** — kończy aukcje, wysyła maile

Logowanie wymagane do licytacji, dodawania aukcji i watchlist.

---

## 5. Bezpieczeństwo

- Hasła hashowane (Django)
- CSRF na formularzach
- Licytacja tylko po zalogowaniu
- Sprzedawca nie licytuje własnej aukcji
- Tylko właściciel usuwa swoją aukcję

---

## 6. Testy

```bash
uv run python manage.py test
```

18 testów automatycznych — wszystkie OK.

---

## 7. Instrukcja obsługi

### Uruchomienie

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py seed_categories
uv run python manage.py seed_demo
uv run python manage.py runserver
```

Strona: http://127.0.0.1:8000/

Konta demo: `sprzedawca1` / `kupujacy1` — hasło: `demo12345`

### Użytkowanie

1. Zarejestruj się lub zaloguj
2. Dodaj aukcję (sprzedawca)
3. Złóż ofertę na aukcji (kupujący)
4. Kliknij **Obserwuj** dla powiadomień
5. Zakończ aukcje: `uv run python manage.py end_auctions`

---

## 8. Wymagania systemowe

| Element | Minimum |
|---------|---------|
| Python | 3.14+ |
| uv | najnowszy |
| Przeglądarka | Chrome / Firefox / Safari |

---

*Wersja DOCX: `docs/dokumentacja-projektu.docx` — generuj: `uv run python scripts/generate_docx.py`*
