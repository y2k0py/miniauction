from django.db import transaction
from django.utils import timezone

from notifications.services import (
    notify_auction_ended,
    notify_new_bid_on_watched_auction,
)

from .models import Auction, Bid


@transaction.atomic
def place_bid(auction: Auction, bidder, amount) -> Bid:
    auction = Auction.objects.select_for_update().get(pk=auction.pk)

    bid = Bid(auction=auction, bidder=bidder, amount=amount)
    bid.full_clean()
    bid.save()

    auction.current_price = amount
    auction.save(update_fields=["current_price", "updated_at"])

    notify_new_bid_on_watched_auction(auction, bid)
    return bid


def end_expired_auctions() -> int:
    now = timezone.now()
    expired = Auction.objects.filter(
        status=Auction.Status.ACTIVE,
        ends_at__lte=now,
    )

    count = 0
    for auction in expired:
        with transaction.atomic():
            highest = auction.get_highest_bid()
            auction.status = Auction.Status.ENDED
            auction.winner = highest.bidder if highest else None
            auction.save(update_fields=["status", "winner", "updated_at"])
            notify_auction_ended(auction)
            count += 1

    return count
