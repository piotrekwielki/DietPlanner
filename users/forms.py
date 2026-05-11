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
    auto_target_fields = (
        "daily_calorie_limit",
        "daily_protein_limit",
        "daily_fat_limit",
        "daily_carbs_limit",
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in (
            "age",
            "height_cm",
            "weight_kg",
            "activity_level",
            "goal",
        ):
            self.fields[field_name].widget.attrs["data-target-source"] = "true"

        for field_name in self.auto_target_fields:
            self.fields[field_name].widget.attrs["data-auto-target"] = "true"

    def save(self, commit=True):
        profile = super().save(commit=False)
        if not any(field in self.changed_data for field in self.auto_target_fields):
            for field_name, value in profile.calculate_nutrition_targets().items():
                setattr(profile, field_name, value)

        if commit:
            profile.save()
            self.save_m2m()
        return profile
