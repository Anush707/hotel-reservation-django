from datetime import date, timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from hotel.models import Reservation, Room


class HotelCustomerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="guest1",
            email="guest1@example.com",
            password="StrongPassword123!",
        )
        self.room1 = Room.objects.create(
            room_number="101",
            room_type="single",
            capacity=1,
            price_per_night=85.00,
        )
        self.room2 = Room.objects.create(
            room_number="202",
            room_type="suite",
            capacity=3,
            price_per_night=190.00,
        )
        self.check_in = date.today() + timedelta(days=5)
        self.check_out = date.today() + timedelta(days=8)

    def test_invalid_reservation_dates_raise_error(self):
        """Check-out before check-in must raise a ValidationError."""
        reservation = Reservation(
            user=self.user,
            room=self.room1,
            check_in=self.check_out,
            check_out=self.check_in,
        )
        with self.assertRaises(ValidationError):
            reservation.save()

    def test_overlapping_reservation_blocked(self):
        """Booking the same room for overlapping dates must be blocked."""
        Reservation.objects.create(
            user=self.user,
            room=self.room1,
            check_in=self.check_in,
            check_out=self.check_out,
        )
        overlapping = Reservation(
            user=self.user,
            room=self.room1,
            check_in=self.check_in + timedelta(days=1),
            check_out=self.check_out + timedelta(days=1),
        )
        with self.assertRaises(ValidationError):
            overlapping.save()

    def test_home_filters_out_booked_rooms(self):
        """Search results must hide rooms already confirmed for those dates."""
        Reservation.objects.create(
            user=self.user,
            room=self.room1,
            check_in=self.check_in,
            check_out=self.check_out,
        )
        response = self.client.get(
            reverse("home"),
            {
                "check_in": self.check_in.isoformat(),
                "check_out": self.check_out.isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Room 101")
        self.assertContains(response, "Room 202")

    def test_unauthenticated_user_redirected_from_booking(self):
        """Guests who are not logged in must be redirected to login."""
        response = self.client.get(reverse("book_room", args=[self.room1.id]))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_book_room(self):
        """Logged-in users can book an available room and get redirected."""
        self.client.login(username="guest1", password="StrongPassword123!")
        response = self.client.post(
            reverse("book_room", args=[self.room1.id]),
            {
                "check_in": self.check_in.isoformat(),
                "check_out": self.check_out.isoformat(),
            },
        )
        self.assertRedirects(response, reverse("my_reservations"))
        self.assertEqual(
            Reservation.objects.filter(user=self.user, room=self.room1).count(), 1
        )

    def test_user_can_cancel_own_reservation(self):
        """Logged-in users can cancel their own confirmed reservation."""
        reservation = Reservation.objects.create(
            user=self.user,
            room=self.room1,
            check_in=self.check_in,
            check_out=self.check_out,
        )
        self.client.login(username="guest1", password="StrongPassword123!")
        response = self.client.post(
            reverse("cancel_reservation", args=[reservation.id])
        )
        self.assertRedirects(response, reverse("my_reservations"))
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, "cancelled")