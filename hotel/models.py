from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Room(models.Model):
    ROOM_TYPES = [
        ("single", "Single"),
        ("double", "Double"),
        ("suite", "Suite"),
    ]

    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default="single")
    capacity = models.PositiveIntegerField(default=1)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["room_number"]

    def __str__(self):
        return f"Room {self.room_number} ({self.get_room_type_display()})"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="confirmed",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.check_in and self.check_out:
            if self.check_out <= self.check_in:
                raise ValidationError("Check-out date must be after check-in date.")

            if self.room_id and self.status == "confirmed":
                overlapping = Reservation.objects.filter(
                    room=self.room,
                    status="confirmed",
                    check_in__lt=self.check_out,
                    check_out__gt=self.check_in,
                ).exclude(pk=self.pk)

                if overlapping.exists():
                    raise ValidationError("This room is already booked for those dates.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - Room {self.room.room_number} ({self.check_in} to {self.check_out})"