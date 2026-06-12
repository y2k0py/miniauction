# Diagram przypadków użycia — MiniAukcje

```mermaid
flowchart LR
    subgraph actors [Aktorzy]
        Guest[Gosc]
        User[Uzytkownik]
        Seller[Sprzedawca]
        Admin[Administrator]
        System[System]
    end

    subgraph usecases [Przypadki uzycia]
        UC01[UC01 Rejestracja]
        UC02[UC02 Logowanie]
        UC03[UC03 Przegladanie aukcji]
        UC04[UC04 Filtrowanie kategorii]
        UC05[UC05 Wyszukiwanie]
        UC06[UC06 Tworzenie aukcji]
        UC07[UC07 Skladanie oferty]
        UC08[UC08 Watchlist]
        UC09[UC09 Profil]
        UC10[UC10 Powiadomienie email]
        UC11[UC11 Zakonczenie aukcji]
        UC12[UC12 Panel admin]
    end

    Guest --> UC01
    Guest --> UC02
    Guest --> UC03
    Guest --> UC04
    Guest --> UC05

    User --> UC02
    User --> UC03
    User --> UC07
    User --> UC08
    User --> UC09

    Seller --> UC06
    Seller --> UC09

    Admin --> UC12

    System --> UC11
    System --> UC10

    UC07 -.->|include| UC02
    UC06 -.->|include| UC02
    UC08 -.->|include| UC02
    UC11 -.->|include| UC10
```

## Legenda relacji

- **include** (linia przerywana): przypadek bazowy wymaga wykonania innego UC
- Sprzedawca i Użytkownik dziedziczą po roli zarejestrowanego użytkownika
