from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AuctionForm, BidForm
from .models import Auction, Category, Watchlist
from .services import end_expired_auctions, place_bid


def auction_list(request):
    end_expired_auctions()

    auctions = Auction.objects.select_related("seller", "category").filter(
        status=Auction.Status.ACTIVE
    )
    categories = Category.objects.all()
    category_slug = request.GET.get("kategoria")
    query = request.GET.get("q", "").strip()

    if category_slug:
        auctions = auctions.filter(category__slug=category_slug)
    if query:
        auctions = auctions.filter(Q(title__icontains=query) | Q(description__icontains=query))

    watched_ids = set()
    if request.user.is_authenticated:
        watched_ids = set(
            Watchlist.objects.filter(user=request.user).values_list("auction_id", flat=True)
        )

    return render(
        request,
        "auctions/list.html",
        {
            "auctions": auctions,
            "categories": categories,
            "active_category": category_slug,
            "query": query,
            "watched_ids": watched_ids,
        },
    )


def auction_detail(request, pk):
    end_expired_auctions()
    auction = get_object_or_404(
        Auction.objects.select_related("seller", "category", "winner"),
        pk=pk,
    )
    bids = auction.bids.select_related("bidder")[:20]
    is_watched = False
    bid_form = None

    if request.user.is_authenticated:
        is_watched = Watchlist.objects.filter(user=request.user, auction=auction).exists()
        if auction.is_active and auction.seller != request.user:
            bid_form = BidForm(auction=auction, bidder=request.user)

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={request.path}")
        if bid_form is None:
            messages.error(request, "Nie możesz licytować tej aukcji.")
            return redirect("auctions:detail", pk=pk)
        bid_form = BidForm(request.POST, auction=auction, bidder=request.user)
        if bid_form.is_valid():
            try:
                place_bid(auction, request.user, bid_form.cleaned_data["amount"])
                messages.success(request, "Oferta została złożona.")
                return redirect("auctions:detail", pk=pk)
            except ValidationError as exc:
                if hasattr(exc, "message_dict"):
                    for field, errs in exc.message_dict.items():
                        for err in errs:
                            bid_form.add_error(field if field in bid_form.fields else None, err)
                else:
                    bid_form.add_error(None, exc.message)

    return render(
        request,
        "auctions/detail.html",
        {
            "auction": auction,
            "bids": bids,
            "bid_form": bid_form,
            "is_watched": is_watched,
        },
    )


@login_required
def auction_create(request):
    if request.method == "POST":
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.seller = request.user
            auction.current_price = auction.starting_price
            auction.save()
            messages.success(request, "Aukcja została utworzona.")
            return redirect("auctions:detail", pk=auction.pk)
    else:
        form = AuctionForm()

    return render(request, "auctions/create.html", {"form": form})


@login_required
def toggle_watchlist(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    item, created = Watchlist.objects.get_or_create(user=request.user, auction=auction)
    if not created:
        item.delete()
        messages.info(request, "Usunięto z listy obserwowanych.")
    else:
        messages.success(request, "Dodano do listy obserwowanych.")
    return redirect("auctions:detail", pk=pk)


@login_required
def auction_delete(request, pk):
    auction = get_object_or_404(Auction, pk=pk)

    if auction.seller != request.user:
        messages.error(request, "Nie możesz usunąć cudzej aukcji.")
        return redirect("auctions:detail", pk=pk)

    if auction.bids.exists():
        messages.error(request, "Nie można usunąć aukcji, która ma już oferty.")
        return redirect("auctions:detail", pk=pk)

    if request.method == "POST":
        auction.delete()
        messages.success(request, "Aukcja została usunięta.")
        return redirect("accounts:profile")

    return render(request, "auctions/delete_confirm.html", {"auction": auction})
