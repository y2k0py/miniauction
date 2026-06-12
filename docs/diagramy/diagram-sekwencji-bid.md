# Diagram sekwencji — składanie oferty

```mermaid
sequenceDiagram
    actor Kupujacy as Kupujacy
    participant View as auction_detail
    participant Form as BidForm
    participant Service as place_bid
    participant DB as SQLite
    participant Notify as notifications

    Kupujacy->>View: POST /aukcja/id/ (amount)
    View->>View: Sprawdz login
    View->>Form: is_valid()
    Form->>Form: Walidacja amount > current_price
    Form-->>View: OK
    View->>Service: place_bid(auction, user, amount)
    Service->>DB: SELECT FOR UPDATE auction
    Service->>DB: INSERT bid
    Service->>DB: UPDATE current_price
    Service->>Notify: notify_new_bid_on_watched_auction()
    Notify->>Notify: send_mail do obserwujacych
    Service-->>View: bid
    View-->>Kupujacy: Redirect + komunikat sukcesu
```

## Kroki

1. Użytkownik wysyła formularz z kwotą oferty.
2. Widok sprawdza autentykację i waliduje formularz.
3. Serwis `place_bid` w transakcji zapisuje ofertę i aktualizuje cenę.
4. Moduł powiadomień wysyła e-mail do obserwujących.
5. Użytkownik wraca na stronę aukcji z komunikatem.
