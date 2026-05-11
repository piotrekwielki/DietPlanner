from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify


class Ingredient(models.Model):
    CATEGORY_CHOICES = [
        ("vegetables", "Warzywa"),
        ("fruit", "Owoce"),
        ("dairy", "Nabiał"),
        ("meat", "Mięso"),
        ("grains", "Produkty zbożowe"),
        ("dry", "Produkty suche"),
        ("other", "Inne"),
    ]

    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    default_unit = models.CharField(max_length=30, default="g")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Meal(models.Model):
    PREFERRED_MEAL_TIME_CHOICES = [
        ("any", "Dowolna pora"),
        ("breakfast", "Śniadanie"),
        ("lunch", "Lunch"),
        ("dinner", "Obiad"),
        ("snack", "Przekąska"),
        ("supper", "Kolacja"),
    ]
    DIET_CHOICES = [
        ("standard", "Standard"),
        ("vegetarian", "Wegetariańskie"),
        ("vegan", "Wegańskie"),
        ("gluten_free", "Bez glutenu"),
        ("lactose_free", "Bez laktozy"),
    ]

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField()
    calories = models.DecimalField(max_digits=7, decimal_places=2, help_text="Na 1 porcję")
    protein = models.DecimalField(max_digits=7, decimal_places=2, help_text="Na 1 porcję")
    fat = models.DecimalField(max_digits=7, decimal_places=2, help_text="Na 1 porcję")
    carbs = models.DecimalField(max_digits=7, decimal_places=2, help_text="Na 1 porcję")
    servings = models.PositiveIntegerField(default=1, help_text="Liczba porcji w przepisie")
    diet_type = models.CharField(max_length=20, choices=DIET_CHOICES, default="standard")
    preferred_meal_time = models.CharField(
        max_length=120, default="any", help_text="Mozesz wybrac kilka por posilku."
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_meals"
    )
    is_public = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def preferred_meal_time_values(self):
        values = [value for value in self.preferred_meal_time.split(",") if value]
        return values or ["any"]

    def matches_meal_time(self, meal_time):
        values = self.preferred_meal_time_values()
        return "any" in values or meal_time in values

    def preferred_meal_time_display(self):
        labels = dict(self.PREFERRED_MEAL_TIME_CHOICES)
        return ", ".join(labels.get(value, value) for value in self.preferred_meal_time_values())


class MealIngredient(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="meal_ingredients")
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="ingredient_meals"
    )
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=30, default="g")

    class Meta:
        unique_together = ("meal", "ingredient")
        ordering = ["ingredient__name"]

    def __str__(self):
        return f"{self.ingredient.name} - {self.meal.name}"


class FavoriteMeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_meals")
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "meal")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.meal.name}"
