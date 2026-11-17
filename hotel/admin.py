from django.contrib import admin
from .models import Room, Reservation


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("room_number", "room_type", "capacity", "price_per_night", "is_active")
    list_filter = ("room_type", "is_active")
    search_fields = ("room_number", "description")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "room", "check_in", "check_out", "status", "created_at")
    list_filter = ("status", "check_in", "check_out")
    search_fields = ("user__username", "room__room_number")