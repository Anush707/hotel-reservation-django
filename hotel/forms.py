from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reservation


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ("check_in", "check_out")
        widgets = {
            "check_in": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "check_out": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }