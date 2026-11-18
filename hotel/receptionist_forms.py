
from django import forms
from .models import Reservation, Room


class ReservationUpdateForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ("room", "check_in", "check_out", "status")

        widgets = {
            "room": forms.Select(attrs={"class": "form-select"}),
            "check_in": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "check_out": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["room"].queryset = Room.objects.filter(is_active=True)
