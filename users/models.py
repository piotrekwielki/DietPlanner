from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ACTIVITY_CHOICES = [
        ("low", "Niska aktywność"),
        ("moderate", "Średnia aktywność"),
        ("high", "Wysoka aktywność"),
    ]
    GOAL_CHOICES = [
        ("cut", "Redukcja"),
        ("maintain", "Utrzymanie"),
        ("bulk", "Masa"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    age = models.PositiveIntegerField(default=25)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, default=170)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, default=70)
    activity_level = models.CharField(
        max_length=20, choices=ACTIVITY_CHOICES, default="moderate"
    )
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default="maintain")
    daily_calorie_limit = models.PositiveIntegerField(default=2200)
    daily_protein_limit = models.PositiveIntegerField(default=120)
    daily_fat_limit = models.PositiveIntegerField(default=70)
    daily_carbs_limit = models.PositiveIntegerField(default=250)

    def __str__(self):
        return f"Profil: {self.user.username}"

    @property
    def bmi(self):
        height_m = float(self.height_cm) / 100
        if not height_m:
            return 0
        return round(float(self.weight_kg) / (height_m**2), 2)

    @property
    def bmr(self):
        return round(10 * float(self.weight_kg) + 6.25 * float(self.height_cm) - 5 * self.age + 5, 2)

    @property
    def tdee(self):
        multiplier = {"low": 1.2, "moderate": 1.55, "high": 1.725}.get(
            self.activity_level, 1.55
        )
        return round(self.bmr * multiplier, 2)

    def calculate_nutrition_targets(self):
        goal_multiplier = {
            "cut": 0.85,
            "maintain": 1,
            "bulk": 1.1,
        }.get(self.goal, 1)

        calories = max(round(self.tdee * goal_multiplier), 1)
        protein = max(round(float(self.weight_kg) * 1.8), 1)
        fat = max(round((calories * 0.25) / 9), 1)
        carbs = max(round((calories - protein * 4 - fat * 9) / 4), 1)

        return {
            "daily_calorie_limit": calories,
            "daily_protein_limit": protein,
            "daily_fat_limit": fat,
            "daily_carbs_limit": carbs,
        }
