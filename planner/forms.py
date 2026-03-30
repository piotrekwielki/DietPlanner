from django import forms
from django.db.models import Q

from meals.models import Meal

from .models import PlanTemplate, PlannedMeal


class PlannedMealForm(forms.ModelForm):
    class Meta:
        model = PlannedMeal
        fields = ("meal", "meal_time", "servings", "notes")

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Meal.objects.filter(is_public=True, is_approved=True)
        if user and user.is_authenticated:
            queryset = Meal.objects.filter(Q(is_public=True, is_approved=True) | Q(created_by=user))
        self.fields["meal"].queryset = queryset.order_by("name")


class CopyDayForm(forms.Form):
    source_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    target_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))


class TemplateApplyForm(forms.Form):
    template = forms.ModelChoiceField(queryset=PlanTemplate.objects.none(), label="Szablon")
    target_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = PlanTemplate.objects.filter(is_public=True)
        if user and user.is_authenticated:
            queryset = PlanTemplate.objects.filter(Q(is_public=True) | Q(created_by=user))
        self.fields["template"].queryset = queryset
