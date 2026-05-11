from django import forms
from django.forms import ModelForm, inlineformset_factory

from .models import Meal, MealIngredient


class MealForm(ModelForm):
    preferred_meal_time = forms.MultipleChoiceField(
        choices=Meal.PREFERRED_MEAL_TIME_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Preferowana pora posilku",
    )

    class Meta:
        model = Meal
        fields = (
            "name",
            "description",
            "calories",
            "protein",
            "fat",
            "carbs",
            "servings",
            "diet_type",
            "preferred_meal_time",
            "is_public",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial["preferred_meal_time"] = self.instance.preferred_meal_time_values()

    def clean_preferred_meal_time(self):
        values = self.cleaned_data["preferred_meal_time"] or ["any"]
        if "any" in values and len(values) > 1:
            values = [value for value in values if value != "any"]
        return ",".join(values)


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
