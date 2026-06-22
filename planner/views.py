import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from meals.models import Meal

from .forms import CopyDayForm, PlannedMealForm, TemplateApplyForm
from .models import DailyPlan, PlannedMeal, PlanTemplateMeal


MEAL_TIME_TARGETS = [
    ("breakfast", Decimal("0.25")),
    ("lunch", Decimal("0.15")),
    ("dinner", Decimal("0.35")),
    ("snack", Decimal("0.10")),
    ("supper", Decimal("0.15")),
]


def visible_meals_for_user(user):
    return Meal.objects.filter(Q(is_public=True, is_approved=True) | Q(created_by=user))


def serving_options():
    return [Decimal(value) / Decimal("4") for value in range(2, 9)]


def score_meal(meal, meal_time, servings, targets, used_meal_ids):
    calories = meal.calories * servings
    protein = meal.protein * servings
    fat = meal.fat * servings
    carbs = meal.carbs * servings

    score = (
        abs(calories - targets["calories"]) / max(targets["calories"], Decimal("1"))
        + abs(protein - targets["protein"]) / max(targets["protein"], Decimal("1"))
        + abs(fat - targets["fat"]) / max(targets["fat"], Decimal("1"))
        + abs(carbs - targets["carbs"]) / max(targets["carbs"], Decimal("1"))
    )

    if not meal.matches_meal_time(meal_time):
        score += Decimal("0.75")
    if meal.id in used_meal_ids:
        score += Decimal("0.20")
    return score


def choose_meal_for_slot(meals, meal_time, slot_share, profile, used_meal_ids):
    targets = {
        "calories": Decimal(profile.daily_calorie_limit) * slot_share,
        "protein": Decimal(profile.daily_protein_limit) * slot_share,
        "fat": Decimal(profile.daily_fat_limit) * slot_share,
        "carbs": Decimal(profile.daily_carbs_limit) * slot_share,
    }
    preferred = [meal for meal in meals if meal.matches_meal_time(meal_time)]
    candidates = preferred or meals

    scored_options = []
    for meal in candidates:
        for servings in serving_options():
            score = score_meal(meal, meal_time, servings, targets, used_meal_ids)
            scored_options.append((score, meal, servings))

    if not scored_options:
        return None, Decimal("1")

    scored_options.sort(key=lambda option: option[0])
    shortlist_size = min(5, len(scored_options))
    _, meal, servings = random.choice(scored_options[:shortlist_size])
    return meal, servings


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
    suggestions = visible_meals_for_user(request.user)
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

#TODO limit kalorii nie jest brany pod uwage
@login_required
def generate_week_plan(request):
    if request.method != "POST":
        return redirect("planner:weekly_planner")

    week_start_param = request.POST.get("week_start")
    if week_start_param:
        week_start = datetime.strptime(week_start_param, "%Y-%m-%d").date()
    else:
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())

    meals = list(visible_meals_for_user(request.user).order_by("name"))
    planner_url = f"{reverse('planner:weekly_planner')}?week_start={week_start.isoformat()}"
    if not meals:
        messages.error(request, "Dodaj najpierw dania, aby wygenerowaÄ‡ jadÅ‚ospis.")
        return redirect(planner_url)

    profile = request.user.profile
    used_meal_ids = set()
    for index in range(7):
        day = week_start + timedelta(days=index)
        daily_plan, _ = DailyPlan.objects.get_or_create(user=request.user, date=day)
        daily_plan.planned_meals.all().delete()

        for meal_time, slot_share in MEAL_TIME_TARGETS:
            meal, servings = choose_meal_for_slot(
                meals, meal_time, slot_share, profile, used_meal_ids
            )
            if meal is None:
                continue
            PlannedMeal.objects.create(
                daily_plan=daily_plan,
                meal=meal,
                meal_time=meal_time,
                servings=servings,
            )
            used_meal_ids.add(meal.id)

    messages.success(request, "Tygodniowy jadłospis został wygenerowany.")
    return redirect(planner_url)


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
