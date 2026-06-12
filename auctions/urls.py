from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.auction_list, name="list"),
    path("nowa/", views.auction_create, name="create"),
    path("<int:pk>/", views.auction_detail, name="detail"),
    path("<int:pk>/obserwuj/", views.toggle_watchlist, name="toggle_watchlist"),
    path("<int:pk>/usun/", views.auction_delete, name="delete"),
]
