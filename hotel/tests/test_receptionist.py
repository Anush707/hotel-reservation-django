
from datetime import date, timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from hotel.models import Room, Reservation


class ReceptionistTests(TestCase):

    def setUp(self):
        # Create the Receptionist group
        self.receptionist_group, _ = Group.objects.get_or_create(
            name="Receptionist"
        )

        # Create a receptionist user
        self.receptionist = User.objects.create_user(
            username="receptionist",
            password="testpassword123"
        )
        self.receptionist.groups.add(self.receptionist_group)

        # Create a normal customer
        self.customer = User.objects.create_user(
            username="customer",
            password="testpassword123"
        )
        #testing CICD
        # Create two rooms
        self.room1 = Room.objects.create(
            room_number="101",
            room_type="single",
            capacity=1,
            price_per_night="75.00",
        )

        self.room2 = Room.objects.create(
            room_number="102",
            room_type="double",
            capacity=2,
            price_per_night="120.00",
        )

        # Create a reservation
        self.reservation = Reservation.objects.create(
            user=self.customer,
            room=self.room1,
            check_in=date.today() + timedelta(days=10),
            check_out=date.today() + timedelta(days=15),
            status="confirmed",
        )

    def test_receptionist_can_access_dashboard(self):
        self.client.login(
            username="receptionist",
            password="testpassword123"
        )

        response = self.client.get(
            reverse("receptionist_dashboard")
        )

        self.assertEqual(response.status_code, 200)

    def test_customer_cannot_access_dashboard(self):
        self.client.login(
            username="customer",
            password="testpassword123"
        )

        response = self.client.get(
            reverse("receptionist_dashboard")
        )

        self.assertEqual(response.status_code, 403)

    def test_receptionist_can_update_reservation(self):
        self.client.login(
            username="receptionist",
            password="testpassword123"
        )

        response = self.client.post(
            reverse(
                "edit_reservation",
                args=[self.reservation.id]
            ),
            {
                "room": self.room2.id,
                "check_in": self.reservation.check_in,
                "check_out": self.reservation.check_out,
                "status": "confirmed",
            },
        )

        self.assertEqual(response.status_code, 302)

        self.reservation.refresh_from_db()

        self.assertEqual(self.reservation.room, self.room2)

    def test_receptionist_can_cancel_reservation(self):
        self.client.login(
            username="receptionist",
            password="testpassword123"
        )

        self.client.post(
            reverse(
                "edit_reservation",
                args=[self.reservation.id]
            ),
            {
                "room": self.room1.id,
                "check_in": self.reservation.check_in,
                "check_out": self.reservation.check_out,
                "status": "cancelled",
            },
        )

        self.reservation.refresh_from_db()

        self.assertEqual(
            self.reservation.status,
            "cancelled"
        )
