from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render
from .forms import SignUpForm


def home(request):
    return render(request, "hotel/base.html")


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