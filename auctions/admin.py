from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Auction, Bid, Category, Watchlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    readonly_fields = ("bidder", "amount", "created_at")


@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ("title", "seller", "category", "current_price", "status", "ends_at")
    list_filter = ("status", "category")
    search_fields = ("title", "seller__username")
    inlines = [BidInline]


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ("auction", "bidder", "amount", "created_at")
    search_fields = ("auction__title", "bidder__username")


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "auction", "created_at")


admin.site.unregister(User)
admin.site.register(User, BaseUserAdmin)
