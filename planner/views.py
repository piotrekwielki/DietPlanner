from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from meals.models import Meal

from .forms import CopyDayForm, PlannedMealForm, TemplateApplyForm
from .models import DailyPlan, PlannedMeal, PlanTemplateMeal


@login_required
def weekly_planner(request):
    week_start_param = request.GET.get("week_start")
    if week_start_param:
        week_start = datetime.strptime(week_start_param, "%Y-%m-%d").date()
    else:
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())

    week_days = []
    for index in range(7):
        day = week_start + timedelta(days=index)
        plan = (
            DailyPlan.objects.filter(user=request.user, date=day)
            .prefetch_related("planned_meals__meal")
            .first()
        )
        totals = plan.calculate_totals() if plan else DailyPlan.empty_totals()
        week_days.append({"date": day, "plan": plan, "totals": totals})

    return render(
        request,
        "planner/weekly_planner.html",
        {
            "week_days": week_days,
            "week_start": week_start,
            "prev_week": week_start - timedelta(days=7),
            "next_week": week_start + timedelta(days=7),
            "copy_form": CopyDayForm(),
            "template_form": TemplateApplyForm(user=request.user, initial={"target_date": week_start}),
        },
    )


@login_required
def day_detail(request, day):
    selected_date = datetime.strptime(day, "%Y-%m-%d").date()
    daily_plan, _ = DailyPlan.objects.get_or_create(user=request.user, date=selected_date)

    if request.method == "POST":
        form = PlannedMealForm(request.POST, user=request.user)
        if form.is_valid():
            planned = form.save(commit=False)
            planned.daily_plan = daily_plan
            planned.save()
            messages.success(request, "Posiłek został dodany do planu.")
            return redirect("planner:day_detail", day=selected_date.isoformat())
    else:
        form = PlannedMealForm(user=request.user)

    totals = daily_plan.calculate_totals()
    profile = request.user.profile
    remaining = max(profile.daily_calorie_limit - totals["calories"], 0)
    suggestions = Meal.objects.filter(Q(is_public=True, is_approved=True) | Q(created_by=request.user))
    if remaining > 0:
        suggestions = suggestions.filter(calories__lte=remaining)

    return render(
        request,
        "planner/day_detail.html",
        {
            "daily_plan": daily_plan,
            "selected_date": selected_date,
            "planned_meals": daily_plan.planned_meals.select_related("meal"),
            "totals": totals,
            "remaining": remaining,
            "profile": profile,
            "form": form,
            "suggestions": suggestions.order_by("calories")[:5],
        },
    )


@login_required
def copy_day_plan(request):
    if request.method == "POST":
        form = CopyDayForm(request.POST)
        if form.is_valid():
            source_plan = DailyPlan.objects.filter(
                user=request.user, date=form.cleaned_data["source_date"]
            ).first()
            if not source_plan:
                messages.error(request, "Brak planu do skopiowania dla wybranego dnia.")
                return redirect("planner:weekly_planner")

            target_plan, _ = DailyPlan.objects.get_or_create(
                user=request.user, date=form.cleaned_data["target_date"]
            )
            target_plan.planned_meals.all().delete()
            for item in source_plan.planned_meals.all():
                PlannedMeal.objects.create(
                    daily_plan=target_plan,
                    meal=item.meal,
                    meal_time=item.meal_time,
                    servings=item.servings,
                    notes=item.notes,
                )
            messages.success(request, "Plan dnia został skopiowany.")
    return redirect("planner:weekly_planner")


@login_required
def apply_template(request):
    if request.method == "POST":
        form = TemplateApplyForm(request.POST, user=request.user)
        if form.is_valid():
            daily_plan, _ = DailyPlan.objects.get_or_create(
                user=request.user, date=form.cleaned_data["target_date"]
            )
            daily_plan.planned_meals.all().delete()
            for item in PlanTemplateMeal.objects.filter(template=form.cleaned_data["template"]).select_related("meal"):
                PlannedMeal.objects.create(
                    daily_plan=daily_plan,
                    meal=item.meal,
                    meal_time=item.meal_time,
                    servings=item.servings,
                )
            messages.success(request, "Szablon jadłospisu został zastosowany.")
    return redirect("planner:weekly_planner")


@login_required
def remove_planned_meal(request, planned_meal_id):
    planned_meal = get_object_or_404(
        PlannedMeal.objects.select_related("daily_plan"),
        id=planned_meal_id,
        daily_plan__user=request.user,
    )
    day = planned_meal.daily_plan.date.isoformat()
    planned_meal.delete()
    messages.info(request, "Posiłek został usunięty z planu.")
    return redirect("planner:day_detail", day=day)
