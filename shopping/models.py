from django.contrib.auth.models import User
from django.db import models


class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shopping_lists")
    name = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class ShoppingListItem(models.Model):
    CATEGORY_CHOICES = [
        ("vegetables", "Warzywa"),
        ("fruit", "Owoce"),
        ("dairy", "Nabiał"),
        ("meat", "Mięso"),
        ("grains", "Produkty zbożowe"),
        ("dry", "Produkty suche"),
        ("other", "Inne"),
    ]

    shopping_list = models.ForeignKey(
        ShoppingList, on_delete=models.CASCADE, related_name="items"
    )
    ingredient_name = models.CharField(max_length=150)
    total_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=30, default="g")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other")
    is_checked = models.BooleanField(default=False)

    class Meta:
        ordering = ["category", "ingredient_name"]

    def __str__(self):
        return self.ingredient_name
