from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count
from django.shortcuts import render
from django.urls import reverse_lazy

from auctions.models import Auction, Bid, Watchlist

from .forms import RegisterForm


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(
                request,
                "accounts/register_success.html",
                {"username": form.cleaned_data["username"]},
            )
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("auctions:list")


@login_required
def profile(request):
    my_auctions = Auction.objects.filter(seller=request.user).annotate(bid_count=Count("bids"))
    my_bids = Bid.objects.filter(bidder=request.user).select_related("auction")
    watchlist = Watchlist.objects.filter(user=request.user).select_related("auction")
    won_auctions = Auction.objects.filter(winner=request.user, status=Auction.Status.ENDED)

    return render(
        request,
        "accounts/profile.html",
        {
            "my_auctions": my_auctions,
            "my_bids": my_bids,
            "watchlist": watchlist,
            "won_auctions": won_auctions,
        },
    )
