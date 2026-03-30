from django.contrib import admin

from .models import BMIRecord, WeightEntry


@admin.register(WeightEntry)
class WeightEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "weight_kg")
    list_filter = ("date",)


@admin.register(BMIRecord)
class BMIRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "bmi", "bmr", "tdee")
    list_filter = ("date",)
