from datetime import date
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ReservationForm, SignUpForm
from .models import Reservation, Room


def home(request):
    rooms = Room.objects.filter(is_active=True)
    room_type = request.GET.get("room_type", "").strip()
    check_in = request.GET.get("check_in", "").strip()
    check_out = request.GET.get("check_out", "").strip()

    if room_type:
        rooms = rooms.filter(room_type=room_type)

    if check_in and check_out:
        try:
            ci_date = date.fromisoformat(check_in)
            co_date = date.fromisoformat(check_out)
            if co_date > ci_date:
                booked_room_ids = Reservation.objects.filter(
                    status="confirmed",
                    check_in__lt=co_date,
                    check_out__gt=ci_date,
                ).values_list("room_id", flat=True)
                rooms = rooms.exclude(id__in=booked_room_ids)
            else:
                messages.warning(request, "Check-out date must be after check-in date.")
        except ValueError:
            messages.warning(request, "Please enter valid dates.")

    context = {
        "rooms": rooms,
        "room_types": Room.ROOM_TYPES,
        "selected_type": room_type,
        "check_in": check_in,
        "check_out": check_out,
    }
    return render(request, "hotel/room_list.html", context)


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created! Welcome to HotelBooker.")
            return redirect("home")
    else:
        form = SignUpForm()
    return render(request, "hotel/signup.html", {"form": form})


@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id, is_active=True)
    initial_data = {}
    if request.GET.get("check_in"):
        initial_data["check_in"] = request.GET.get("check_in")
    if request.GET.get("check_out"):
        initial_data["check_out"] = request.GET.get("check_out")

    if request.method == "POST":
        form = ReservationForm(request.POST)
        form.instance.user = request.user
        form.instance.room = room
        if form.is_valid():
            form.save()
            messages.success(request, f"Room {room.room_number} booked successfully!")
            return redirect("my_reservations")
    else:
        form = ReservationForm(initial=initial_data)

    return render(request, "hotel/book_room.html", {"room": room, "form": form})


@login_required
def my_reservations(request):
    reservations = request.user.reservations.select_related("room").all()
    return render(request, "hotel/my_reservations.html", {"reservations": reservations})


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    if request.method == "POST" and reservation.status == "confirmed":
        reservation.status = "cancelled"
        reservation.save()
        messages.info(request, f"Reservation for Room {reservation.room.room_number} cancelled.")
    return redirect("my_reservations")