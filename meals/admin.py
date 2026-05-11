from django.contrib import admin

from .models import FavoriteMeal, Ingredient, Meal, MealIngredient


class MealIngredientInline(admin.TabularInline):
    model = MealIngredient
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "default_unit")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "diet_type",
        "preferred_meal_time",
        "calories",
        "is_public",
        "is_approved",
    )
    list_filter = ("diet_type", "preferred_meal_time", "is_public", "is_approved")
    search_fields = ("name", "description")
    inlines = [MealIngredientInline]


@admin.register(FavoriteMeal)
class FavoriteMealAdmin(admin.ModelAdmin):
    list_display = ("user", "meal", "created_at")
