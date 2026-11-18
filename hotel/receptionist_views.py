
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .models import Reservation
from .receptionist_forms import ReservationUpdateForm


def is_receptionist(user):
    return (
        user.is_authenticated
        and (
            user.is_staff
            or user.groups.filter(name="Receptionist").exists()
        )
    )


def receptionist_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not is_receptionist(request.user):
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper


@receptionist_required
def receptionist_dashboard(request):
    reservations = Reservation.objects.select_related(
        "user", "room"
    ).all()

    status = request.GET.get("status")
    room = request.GET.get("room")

    if status in ["confirmed", "cancelled"]:
        reservations = reservations.filter(status=status)

    if room:
        reservations = reservations.filter(
            room__room_number=room
        )

    rooms = Reservation.objects.select_related("room").values_list(
        "room__room_number", flat=True
    ).distinct()

    return render(
        request,
        "hotel/receptionist_dashboard.html",
        {
            "reservations": reservations,
            "rooms": rooms,
            "selected_status": status,
            "selected_room": room,
        },
    )


@receptionist_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    if request.method == "POST":
        form = ReservationUpdateForm(
            request.POST,
            instance=reservation
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Reservation updated successfully."
            )
            return redirect("receptionist_dashboard")

    else:
        form = ReservationUpdateForm(instance=reservation)

    return render(
        request,
        "hotel/receptionist_edit.html",
        {
            "form": form,
            "reservation": reservation
        },
    )
