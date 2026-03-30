from django.contrib import admin

from .models import DailyPlan, PlannedMeal, PlanTemplate, PlanTemplateMeal


class PlannedMealInline(admin.TabularInline):
    model = PlannedMeal
    extra = 0


@admin.register(DailyPlan)
class DailyPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "date")
    list_filter = ("date",)
    inlines = [PlannedMealInline]


class PlanTemplateMealInline(admin.TabularInline):
    model = PlanTemplateMeal
    extra = 1


@admin.register(PlanTemplate)
class PlanTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "calorie_target", "is_public")
    inlines = [PlanTemplateMealInline]
