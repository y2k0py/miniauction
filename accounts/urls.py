from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("rejestracja/", views.register, name="register"),
    path("logowanie/", views.CustomLoginView.as_view(), name="login"),
    path("wylogowanie/", views.CustomLogoutView.as_view(), name="logout"),
    path("profil/", views.profile, name="profile"),
]
