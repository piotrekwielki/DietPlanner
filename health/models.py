from django.contrib.auth.models import User
from django.db import models


class WeightEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="weight_entries")
    date = models.DateField()
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["-date"]
        unique_together = ("user", "date")

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class BMIRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bmi_records")
    date = models.DateField()
    height_cm = models.DecimalField(max_digits=5, decimal_places=2)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    bmi = models.DecimalField(max_digits=5, decimal_places=2)
    bmr = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    tdee = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    class Meta:
        ordering = ["-date"]
        unique_together = ("user", "date")

    def __str__(self):
        return f"BMI {self.user.username} - {self.date}"
