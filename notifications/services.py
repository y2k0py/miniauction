from django.conf import settings
from django.core.mail import send_mail

from auctions.models import Auction, Watchlist


def _send(subject: str, message: str, recipients: list[str]) -> None:
    recipients = [email for email in recipients if email]
    if not recipients:
        return
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )


def notify_new_bid_on_watched_auction(auction: Auction, bid) -> None:
    watchers = (
        Watchlist.objects.filter(auction=auction)
        .exclude(user=bid.bidder)
        .select_related("user")
    )
    recipients = [item.user.email for item in watchers if item.user.email]
    if not recipients:
        return

    subject = f"Nowa oferta na aukcji: {auction.title}"
    message = (
        f"Na obserwowanej aukcji „{auction.title}” pojawiła się nowa oferta.\n\n"
        f"Licytujący: {bid.bidder.username}\n"
        f"Kwota: {bid.amount} PLN\n"
        f"Aktualna cena: {auction.current_price} PLN\n"
    )
    _send(subject, message, recipients)


def notify_auction_ended(auction: Auction) -> None:
    if auction.winner and auction.winner.email:
        _send(
            subject=f"Wygrałeś aukcję: {auction.title}",
            message=(
                f"Gratulacje! Wygrałeś aukcję „{auction.title}”.\n\n"
                f"Twoja wygrywająca oferta: {auction.current_price} PLN\n"
                f"Sprzedawca: {auction.seller.username}\n"
            ),
            recipients=[auction.winner.email],
        )

    if auction.seller.email:
        winner_name = auction.winner.username if auction.winner else "brak ofert"
        _send(
            subject=f"Aukcja zakończona: {auction.title}",
            message=(
                f"Twoja aukcja „{auction.title}” została zakończona.\n\n"
                f"Zwycięzca: {winner_name}\n"
                f"Końcowa cena: {auction.current_price} PLN\n"
            ),
            recipients=[auction.seller.email],
        )

    losing_bidders = set()
    for bid in auction.bids.select_related("bidder"):
        if auction.winner and bid.bidder_id == auction.winner_id:
            continue
        if bid.bidder.email:
            losing_bidders.add((bid.bidder.email, bid.bidder.username))

    for email, username in losing_bidders:
        _send(
            subject=f"Aukcja zakończona: {auction.title}",
            message=(
                f"Aukcja „{auction.title}”, w której brałeś udział, została zakończona.\n\n"
                f"Zwycięzca: {auction.winner.username if auction.winner else 'brak'}\n"
                f"Końcowa cena: {auction.current_price} PLN\n"
            ),
            recipients=[email],
        )
