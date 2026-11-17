from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.signup_view, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="hotel/login.html",
            next_page="home",
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="home"),
        name="logout",
    ),
    path("book/<int:room_id>/", views.book_room, name="book_room"),
    path("my-reservations/", views.my_reservations, name="my_reservations"),
    path("cancel/<int:reservation_id>/", views.cancel_reservation, name="cancel_reservation"),
]