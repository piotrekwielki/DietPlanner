from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm, EmailField, CharField

from .models import UserProfile


class RegisterForm(UserCreationForm):
    email = EmailField(required=True)
    first_name = CharField(max_length=150, required=False)
    last_name = CharField(max_length=150, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")


class UserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")


class ProfileUpdateForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = (
            "age",
            "height_cm",
            "weight_kg",
            "activity_level",
            "goal",
            "daily_calorie_limit",
            "daily_protein_limit",
            "daily_fat_limit",
            "daily_carbs_limit",
        )
