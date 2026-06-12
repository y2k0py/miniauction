from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from auctions.models import Auction, Bid, Category, Watchlist
from auctions.services import end_expired_auctions, place_bid


class AuctionModelTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user("seller", "seller@test.com", "pass12345")
        self.bidder = User.objects.create_user("bidder", "bidder@test.com", "pass12345")
        self.category = Category.objects.create(name="Test", slug="test")

    def _create_auction(self, **kwargs):
        defaults = {
            "seller": self.seller,
            "category": self.category,
            "title": "Test Auction",
            "description": "Opis testowy",
            "starting_price": Decimal("10.00"),
            "current_price": Decimal("10.00"),
            "ends_at": timezone.now() + timedelta(days=1),
        }
        defaults.update(kwargs)
        return Auction.objects.create(**defaults)

    def test_bid_must_exceed_current_price(self):
        auction = self._create_auction()
        bid = Bid(auction=auction, bidder=self.bidder, amount=Decimal("10.00"))
        with self.assertRaises(ValidationError):
            bid.full_clean()

    def test_seller_cannot_bid_on_own_auction(self):
        auction = self._create_auction()
        bid = Bid(auction=auction, bidder=self.seller, amount=Decimal("15.00"))
        with self.assertRaises(ValidationError):
            bid.full_clean()

    def test_place_bid_updates_current_price(self):
        auction = self._create_auction()
        place_bid(auction, self.bidder, Decimal("15.00"))
        auction.refresh_from_db()
        self.assertEqual(auction.current_price, Decimal("15.00"))
        self.assertEqual(auction.bids.count(), 1)

    def test_end_expired_auctions_sets_winner(self):
        auction = self._create_auction()
        place_bid(auction, self.bidder, Decimal("20.00"))
        auction.ends_at = timezone.now() - timedelta(minutes=1)
        auction.save(update_fields=["ends_at"])
        count = end_expired_auctions()
        auction.refresh_from_db()
        self.assertEqual(count, 1)
        self.assertEqual(auction.status, Auction.Status.ENDED)
        self.assertEqual(auction.winner, self.bidder)

    def test_end_auction_without_bids_has_no_winner(self):
        auction = self._create_auction(ends_at=timezone.now() - timedelta(minutes=1))
        end_expired_auctions()
        auction.refresh_from_db()
        self.assertEqual(auction.status, Auction.Status.ENDED)
        self.assertIsNone(auction.winner)


class NotificationTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user("seller", "seller@test.com", "pass12345")
        self.bidder = User.objects.create_user("bidder", "bidder@test.com", "pass12345")
        self.watcher = User.objects.create_user("watcher", "watcher@test.com", "pass12345")
        self.category = Category.objects.create(name="Test", slug="test")
        self.auction = Auction.objects.create(
            seller=self.seller,
            category=self.category,
            title="Watch test",
            description="desc",
            starting_price=Decimal("10.00"),
            current_price=Decimal("10.00"),
            ends_at=timezone.now() + timedelta(days=1),
        )
        Watchlist.objects.create(user=self.watcher, auction=self.auction)

    def test_new_bid_notifies_watchers(self):
        place_bid(self.auction, self.bidder, Decimal("12.00"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.watcher.email, mail.outbox[0].to)

    def test_auction_end_notifies_winner_and_seller(self):
        place_bid(self.auction, self.bidder, Decimal("12.00"))
        self.auction.ends_at = timezone.now() - timedelta(minutes=1)
        self.auction.save(update_fields=["ends_at"])
        mail.outbox.clear()
        end_expired_auctions()
        recipients = {addr for msg in mail.outbox for addr in msg.to}
        self.assertIn(self.bidder.email, recipients)
        self.assertIn(self.seller.email, recipients)


class ViewTests(TestCase):
    def setUp(self):
        self.seller = User.objects.create_user("seller", "seller@test.com", "pass12345")
        self.bidder = User.objects.create_user("bidder", "bidder@test.com", "pass12345")
        self.category = Category.objects.create(name="Test", slug="test")
        self.auction = Auction.objects.create(
            seller=self.seller,
            category=self.category,
            title="View test",
            description="desc",
            starting_price=Decimal("10.00"),
            current_price=Decimal("10.00"),
            ends_at=timezone.now() + timedelta(days=1),
        )

    def test_auction_list_page(self):
        response = self.client.get(reverse("auctions:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View test")

    def test_registration_creates_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "new@test.com",
                "password1": "complexpass123",
                "password2": "complexpass123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_bid_requires_login(self):
        response = self.client.post(
            reverse("auctions:detail", args=[self.auction.pk]),
            {"amount": "15.00"},
        )
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_bid(self):
        self.client.login(username="bidder", password="pass12345")
        response = self.client.post(
            reverse("auctions:detail", args=[self.auction.pk]),
            {"amount": "15.00"},
        )
        self.assertRedirects(response, reverse("auctions:detail", args=[self.auction.pk]))
        self.auction.refresh_from_db()
        self.assertEqual(self.auction.current_price, Decimal("15.00"))

    def test_watchlist_toggle(self):
        self.client.login(username="bidder", password="pass12345")
        url = reverse("auctions:toggle_watchlist", args=[self.auction.pk])
        self.client.post(url)
        self.assertTrue(Watchlist.objects.filter(user=self.bidder, auction=self.auction).exists())
        self.client.post(url)
        self.assertFalse(Watchlist.objects.filter(user=self.bidder, auction=self.auction).exists())

    def test_create_auction_requires_login(self):
        response = self.client.get(reverse("auctions:create"))
        self.assertEqual(response.status_code, 302)

    def test_seller_can_delete_auction_without_bids(self):
        self.client.login(username="seller", password="pass12345")
        response = self.client.post(reverse("auctions:delete", args=[self.auction.pk]))
        self.assertRedirects(response, reverse("accounts:profile"))
        self.assertFalse(Auction.objects.filter(pk=self.auction.pk).exists())

    def test_seller_cannot_delete_auction_with_bids(self):
        Bid.objects.create(auction=self.auction, bidder=self.bidder, amount=Decimal("15.00"))
        self.client.login(username="seller", password="pass12345")
        response = self.client.post(reverse("auctions:delete", args=[self.auction.pk]))
        self.assertRedirects(response, reverse("auctions:detail", args=[self.auction.pk]))
        self.assertTrue(Auction.objects.filter(pk=self.auction.pk).exists())

    def test_non_seller_cannot_delete_auction(self):
        self.client.login(username="bidder", password="pass12345")
        response = self.client.post(reverse("auctions:delete", args=[self.auction.pk]))
        self.assertRedirects(response, reverse("auctions:detail", args=[self.auction.pk]))
        self.assertTrue(Auction.objects.filter(pk=self.auction.pk).exists())
