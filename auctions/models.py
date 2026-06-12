from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Auction(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Aktywna"
        ENDED = "ended", "Zakończona"
        CANCELLED = "cancelled", "Anulowana"

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="auctions",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="auctions",
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="auctions/", blank=True, null=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    ends_at = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    winner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_auctions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "ends_at"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.current_price is None:
            self.current_price = self.starting_price
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE and self.ends_at > timezone.now()

    def clean(self):
        if self.ends_at and self.ends_at <= timezone.now() and self.status == self.Status.ACTIVE:
            raise ValidationError({"ends_at": "Data zakończenia musi być w przyszłości."})
        if self.starting_price < Decimal("0.01"):
            raise ValidationError({"starting_price": "Cena startowa musi być większa od zera."})

    def get_highest_bid(self):
        return self.bids.order_by("-amount", "-created_at").first()


class Bid(models.Model):
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name="bids",
    )
    bidder = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bids",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-amount", "-created_at"]

    def __str__(self):
        return f"{self.bidder.username}: {self.amount} PLN"

    def clean(self):
        if self.amount <= self.auction.current_price:
            raise ValidationError(
                {"amount": f"Oferta musi być wyższa niż {self.auction.current_price} PLN."}
            )
        if self.auction.seller == self.bidder:
            raise ValidationError({"bidder": "Nie możesz licytować własnej aukcji."})
        if not self.auction.is_active:
            raise ValidationError({"auction": "Aukcja nie jest aktywna."})


class Watchlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watchlist_items",
    )
    auction = models.ForeignKey(
        Auction,
        on_delete=models.CASCADE,
        related_name="watchers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["user", "auction"]]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.auction.title}"
