from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower


class ResidentRegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=150, label="First Name")
    last_name = forms.CharField(max_length=150, label="Last Name")
    email = forms.EmailField(max_length=254, label="Email Address")
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", strip=False, widget=forms.PasswordInput)
    address = forms.CharField(max_length=255, widget=forms.Textarea(attrs={"rows": 3}))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("That username is already in use.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.annotate(email_lower=Lower("email")).filter(email_lower=email.lower()).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password1")
        confirmation = cleaned.get("password2")
        if password and confirmation and password != confirmation:
            self.add_error("password2", "The passwords do not match.")
        if password:
            user = User(
                username=cleaned.get("username", ""),
                first_name=cleaned.get("first_name", ""),
                last_name=cleaned.get("last_name", ""),
                email=cleaned.get("email", ""),
            )
            try:
                validate_password(password, user)
            except ValidationError as error:
                self.add_error("password1", error)
        return cleaned
