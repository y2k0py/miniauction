# Diagram klas — MiniAukcje

```mermaid
classDiagram
    class User {
        +int id
        +string username
        +string email
        +string password
    }

    class Category {
        +int id
        +string name
        +string slug
        +save()
    }

    class Auction {
        +int id
        +string title
        +string description
        +decimal starting_price
        +decimal current_price
        +datetime ends_at
        +string status
        +bool is_active
        +get_highest_bid()
    }

    class Bid {
        +int id
        +decimal amount
        +datetime created_at
        +clean()
    }

    class Watchlist {
        +int id
        +datetime created_at
    }

    User "1" --> "*" Auction : seller
    User "1" --> "*" Bid : bidder
    User "1" --> "*" Watchlist : user
    User "1" --> "*" Auction : winner
    Category "1" --> "*" Auction : category
    Auction "1" --> "*" Bid : bids
    Auction "1" --> "*" Watchlist : watchers
```

## Opis klas

| Klasa | Odpowiedzialność |
|-------|------------------|
| `User` | Model Django Auth — konto użytkownika |
| `Category` | Kategoria aukcji (Elektronika, Książki, …) |
| `Auction` | Ogłoszenie aukcyjne ze statusem i ceną |
| `Bid` | Pojedyncza oferta licytacyjna |
| `Watchlist` | Powiązanie użytkownik ↔ obserwowana aukcja |
