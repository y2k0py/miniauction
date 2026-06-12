from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from auctions.models import Auction, Bid, Category, Watchlist


class Command(BaseCommand):
    help = "Tworzy dane demonstracyjne do prezentacji i zrzutów ekranu."

    def handle(self, *args, **options):
        seller, _ = User.objects.get_or_create(
            username="sprzedawca1",
            defaults={"email": "sprzedawca1@demo.pl"},
        )
        seller.set_password("demo12345")
        seller.save()

        buyer, _ = User.objects.get_or_create(
            username="kupujacy1",
            defaults={"email": "kupujacy1@demo.pl"},
        )
        buyer.set_password("demo12345")
        buyer.save()

        category, _ = Category.objects.get_or_create(name="Elektronika")
        ended_category, _ = Category.objects.get_or_create(name="Książki")

        active, created = Auction.objects.get_or_create(
            title="Laptop Dell Inspiron 15",
            defaults={
                "seller": seller,
                "category": category,
                "description": "Laptop w bardzo dobrym stanie, 16 GB RAM, SSD 512 GB. Idealny do nauki i pracy.",
                "starting_price": Decimal("100.00"),
                "current_price": Decimal("120.00"),
                "ends_at": timezone.now() + timedelta(days=2),
                "status": Auction.Status.ACTIVE,
            },
        )
        if created:
            Bid.objects.create(auction=active, bidder=buyer, amount=Decimal("120.00"))
            Watchlist.objects.get_or_create(user=buyer, auction=active)

        Auction.objects.get_or_create(
            title="Kamera GoPro Hero 10",
            defaults={
                "seller": seller,
                "category": category,
                "description": "Kamera sportowa z akcesoriami. Mało używana.",
                "starting_price": Decimal("200.00"),
                "current_price": Decimal("200.00"),
                "ends_at": timezone.now() + timedelta(days=5),
                "status": Auction.Status.ACTIVE,
            },
        )

        ended, created = Auction.objects.get_or_create(
            title="Harry Potter — komplet tomów",
            defaults={
                "seller": seller,
                "category": ended_category,
                "description": "Komplet 7 tomów w twardej oprawie.",
                "starting_price": Decimal("50.00"),
                "current_price": Decimal("75.00"),
                "ends_at": timezone.now() - timedelta(hours=1),
                "status": Auction.Status.ENDED,
                "winner": buyer,
            },
        )
        if created:
            Bid.objects.create(auction=ended, bidder=buyer, amount=Decimal("75.00"))

        self.stdout.write(self.style.SUCCESS("Dane demo utworzone. Konta: sprzedawca1 / kupujacy1 (hasło: demo12345)"))
