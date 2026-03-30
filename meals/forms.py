from django.forms import ModelForm, inlineformset_factory

from .models import Meal, MealIngredient


class MealForm(ModelForm):
    class Meta:
        model = Meal
        fields = (
            "name",
            "description",
            "category",
            "calories",
            "protein",
            "fat",
            "carbs",
            "servings",
            "diet_type",
            "is_public",
        )


class MealIngredientForm(ModelForm):
    class Meta:
        model = MealIngredient
        fields = ("ingredient", "quantity", "unit")


MealIngredientFormSet = inlineformset_factory(
    Meal,
    MealIngredient,
    form=MealIngredientForm,
    extra=3,
    can_delete=True,
)
