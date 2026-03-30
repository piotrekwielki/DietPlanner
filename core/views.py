import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from health.models import BMIRecord, WeightEntry
from meals.models import FavoriteMeal
from planner.models import DailyPlan, PlannedMeal


def home(request):
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    return render(request, "core/home.html")


@login_required
def dashboard(request):
    today = timezone.localdate()
    profile = request.user.profile
    daily_plan = (
        DailyPlan.objects.filter(user=request.user, date=today)
        .prefetch_related("planned_meals__meal")
        .first()
    )
    totals = daily_plan.calculate_totals() if daily_plan else DailyPlan.empty_totals()
    remaining = max(profile.daily_calorie_limit - totals["calories"], 0)

    favorites = FavoriteMeal.objects.filter(user=request.user).select_related("meal")[:4]
    recent_meals = (
        PlannedMeal.objects.filter(daily_plan__user=request.user)
        .select_related("meal", "daily_plan")
        .order_by("-daily_plan__date", "-created_at")[:5]
    )

    chart_dates = []
    chart_calories = []
    for offset in range(6, -1, -1):
        date = today - timedelta(days=offset)
        plan = DailyPlan.objects.filter(user=request.user, date=date).first()
        totals_for_day = plan.calculate_totals() if plan else DailyPlan.empty_totals()
        chart_dates.append(date.strftime("%d.%m"))
        chart_calories.append(float(totals_for_day["calories"]))

    context = {
        "profile": profile,
        "today": today,
        "daily_plan": daily_plan,
        "totals": totals,
        "remaining": remaining,
        "favorites": favorites,
        "recent_meals": recent_meals,
        "latest_bmi": BMIRecord.objects.filter(user=request.user).order_by("-date").first(),
        "latest_weight": WeightEntry.objects.filter(user=request.user).order_by("-date").first(),
        "chart_labels": json.dumps(chart_dates),
        "chart_values": json.dumps(chart_calories),
    }
    return render(request, "core/dashboard.html", context)
