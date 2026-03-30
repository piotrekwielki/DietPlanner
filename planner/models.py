from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models

from meals.models import Meal


class DailyPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_plans")
    date = models.DateField(default=date.today)

    class Meta:
        ordering = ["-date"]
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    @staticmethod
    def empty_totals():
        return {
            "calories": Decimal("0"),
            "protein": Decimal("0"),
            "fat": Decimal("0"),
            "carbs": Decimal("0"),
        }

    def calculate_totals(self):
        totals = self.empty_totals()
        for planned in self.planned_meals.select_related("meal"):
            totals["calories"] += planned.total_calories
            totals["protein"] += planned.total_protein
            totals["fat"] += planned.total_fat
            totals["carbs"] += planned.total_carbs
        return totals


class PlannedMeal(models.Model):
    MEAL_TIME_CHOICES = [
        ("breakfast", "Śniadanie"),
        ("lunch", "Lunch"),
        ("dinner", "Obiad"),
        ("snack", "Przekąska"),
        ("supper", "Kolacja"),
    ]

    daily_plan = models.ForeignKey(
        DailyPlan, on_delete=models.CASCADE, related_name="planned_meals"
    )
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="planned_entries")
    meal_time = models.CharField(max_length=20, choices=MEAL_TIME_CHOICES, default="breakfast")
    servings = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["meal_time", "created_at"]

    def __str__(self):
        return f"{self.daily_plan.date}: {self.meal.name}"

    @property
    def total_calories(self):
        return self.meal.calories * self.servings

    @property
    def total_protein(self):
        return self.meal.protein * self.servings

    @property
    def total_fat(self):
        return self.meal.fat * self.servings

    @property
    def total_carbs(self):
        return self.meal.carbs * self.servings


class PlanTemplate(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    calorie_target = models.PositiveIntegerField(default=2000)
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="plan_templates"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PlanTemplateMeal(models.Model):
    template = models.ForeignKey(
        PlanTemplate, on_delete=models.CASCADE, related_name="template_meals"
    )
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    meal_time = models.CharField(
        max_length=20, choices=PlannedMeal.MEAL_TIME_CHOICES, default="breakfast"
    )
    servings = models.DecimalField(max_digits=5, decimal_places=2, default=1)

    class Meta:
        ordering = ["meal_time", "id"]

    def __str__(self):
        return f"{self.template.name}: {self.meal.name}"
