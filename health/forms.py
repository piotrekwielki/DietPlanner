from django import forms

from .models import WeightEntry


class BMIForm(forms.Form):
    height_cm = forms.DecimalField(max_digits=5, decimal_places=2, label="Wzrost (cm)")
    weight_kg = forms.DecimalField(max_digits=5, decimal_places=2, label="Waga (kg)")
    age = forms.IntegerField(min_value=1, max_value=120, label="Wiek")
    activity_level = forms.ChoiceField(
        choices=[
            ("low", "Niska aktywność"),
            ("moderate", "Średnia aktywność"),
            ("high", "Wysoka aktywność"),
        ],
        label="Aktywność",
    )


class WeightEntryForm(forms.ModelForm):
    class Meta:
        model = WeightEntry
        fields = ("date", "weight_kg")
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
