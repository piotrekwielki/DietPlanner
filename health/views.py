import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import BMIForm, WeightEntryForm
from .models import BMIRecord, WeightEntry


def calculate_metrics(height_cm, weight_kg, age, activity_level):
    height_m = float(height_cm) / 100
    bmi = round(float(weight_kg) / (height_m**2), 2) if height_m else 0
    bmr = round(10 * float(weight_kg) + 6.25 * float(height_cm) - 5 * age + 5, 2)
    multiplier = {"low": 1.2, "moderate": 1.55, "high": 1.725}.get(activity_level, 1.55)
    tdee = round(bmr * multiplier, 2)
    return bmi, bmr, tdee


@login_required
def bmi_calculator(request):
    profile = request.user.profile
    result = None

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "save_weight":
            entry_form = WeightEntryForm(request.POST)
            bmi_form = BMIForm(
                initial={
                    "height_cm": profile.height_cm,
                    "weight_kg": profile.weight_kg,
                    "age": profile.age,
                    "activity_level": profile.activity_level,
                }
            )
            if entry_form.is_valid():
                entry, _ = WeightEntry.objects.update_or_create(
                    user=request.user,
                    date=entry_form.cleaned_data["date"],
                    defaults={"weight_kg": entry_form.cleaned_data["weight_kg"]},
                )
                profile.weight_kg = entry.weight_kg
                profile.save(update_fields=["weight_kg"])
                bmi, bmr, tdee = calculate_metrics(
                    profile.height_cm, entry.weight_kg, profile.age, profile.activity_level
                )
                BMIRecord.objects.update_or_create(
                    user=request.user,
                    date=entry.date,
                    defaults={
                        "height_cm": profile.height_cm,
                        "weight_kg": entry.weight_kg,
                        "bmi": bmi,
                        "bmr": bmr,
                        "tdee": tdee,
                    },
                )
                messages.success(request, "Zapisano nowy wpis wagi i BMI.")
                return redirect("health:bmi_calculator")
        else:
            bmi_form = BMIForm(request.POST)
            entry_form = WeightEntryForm(initial={"date": timezone.localdate()})
            if bmi_form.is_valid():
                result = dict(
                    zip(
                        ["bmi", "bmr", "tdee"],
                        calculate_metrics(
                            bmi_form.cleaned_data["height_cm"],
                            bmi_form.cleaned_data["weight_kg"],
                            bmi_form.cleaned_data["age"],
                            bmi_form.cleaned_data["activity_level"],
                        ),
                    )
                )
    else:
        bmi_form = BMIForm(
            initial={
                "height_cm": profile.height_cm,
                "weight_kg": profile.weight_kg,
                "age": profile.age,
                "activity_level": profile.activity_level,
            }
        )
        entry_form = WeightEntryForm(initial={"date": timezone.localdate(), "weight_kg": profile.weight_kg})

    records = BMIRecord.objects.filter(user=request.user).order_by("date")
    chart_labels = [record.date.strftime("%d.%m") for record in records]
    chart_values = [float(record.bmi) for record in records]

    return render(
        request,
        "health/bmi_calculator.html",
        {
            "bmi_form": bmi_form,
            "entry_form": entry_form,
            "result": result,
            "records": records.order_by("-date")[:10],
            "chart_labels": json.dumps(chart_labels),
            "chart_values": json.dumps(chart_values),
        },
    )
