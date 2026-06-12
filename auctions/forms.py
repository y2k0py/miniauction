from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Auction, Bid


class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ("title", "description", "category", "starting_price", "ends_at", "image")
        labels = {
            "title": "Tytuł",
            "description": "Opis",
            "category": "Kategoria",
            "starting_price": "Cena startowa (PLN)",
            "ends_at": "Data zakończenia",
            "image": "Zdjęcie (opcjonalnie)",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "starting_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "ends_at": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"},
                format="%Y-%m-%dT%H:%M",
            ),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ends_at"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]

    def clean_ends_at(self):
        ends_at = self.cleaned_data["ends_at"]
        if ends_at <= timezone.now():
            raise forms.ValidationError("Data zakończenia musi być w przyszłości.")
        if ends_at > timezone.now() + timedelta(days=30):
            raise forms.ValidationError("Aukcja może trwać maksymalnie 30 dni.")
        return ends_at


class BidForm(forms.Form):
    amount = forms.DecimalField(
        label="Twoja oferta (PLN)",
        min_value=0.01,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
    )

    def __init__(self, *args, auction=None, bidder=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.auction = auction
        self.bidder = bidder

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if not self.auction or not self.bidder:
            return amount

        bid = Bid(auction=self.auction, bidder=self.bidder, amount=amount)
        try:
            bid.full_clean()
        except ValidationError as exc:
            if hasattr(exc, "message_dict"):
                for field, errors in exc.message_dict.items():
                    if field == "amount":
                        raise forms.ValidationError(errors[0])
                    raise forms.ValidationError(errors[0])
            raise forms.ValidationError(exc.message)
        return amount
