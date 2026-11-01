from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.shortcuts import redirect, render

from .forms import ResidentRegistrationForm
from .models import Profile


def register(request):
    if request.method == "POST":
        form = ResidentRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=data["username"],
                        email=data["email"],
                        password=data["password1"],
                        first_name=data["first_name"],
                        last_name=data["last_name"],
                    )
                    Profile.objects.create(user=user, address=data["address"], role="resident")
            except IntegrityError:
                # Unique database constraints close races between validation and insert.
                form.add_error(None, "That username or email address is already in use. Please review your details.")
            else:
                messages.success(request, "Your resident account has been created. You can now sign in.")
                return redirect("login")
    else:
        form = ResidentRegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


def login_destination(request):
    """Minimal destination until the sign-in feature is implemented."""
    return render(request, "accounts/login_placeholder.html")
