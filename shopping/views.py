from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from planner.models import DailyPlan

from .forms import ShoppingRangeForm
from .models import ShoppingList, ShoppingListItem


def build_shopping_list(user, start_date, end_date):
    shopping_list = ShoppingList.objects.create(
        user=user,
        name=f"Lista zakupów {start_date} - {end_date}",
        start_date=start_date,
        end_date=end_date,
    )

    ingredients_map = defaultdict(lambda: {"quantity": Decimal("0"), "unit": "", "category": "other"})
    plans = (
        DailyPlan.objects.filter(user=user, date__range=[start_date, end_date])
        .prefetch_related("planned_meals__meal__meal_ingredients__ingredient")
    )
    for plan in plans:
        for planned in plan.planned_meals.all():
            ratio = planned.servings / planned.meal.servings if planned.meal.servings else 1
            for meal_ingredient in planned.meal.meal_ingredients.all():
                key = meal_ingredient.ingredient.name
                ingredients_map[key]["quantity"] += meal_ingredient.quantity * ratio
                ingredients_map[key]["unit"] = meal_ingredient.unit or meal_ingredient.ingredient.default_unit
                ingredients_map[key]["category"] = meal_ingredient.ingredient.category

    for name, data in ingredients_map.items():
        ShoppingListItem.objects.create(
            shopping_list=shopping_list,
            ingredient_name=name,
            total_quantity=data["quantity"],
            unit=data["unit"],
            category=data["category"],
        )
    return shopping_list


@login_required
def shopping_list_view(request):
    today = timezone.localdate()
    default_end = today + timedelta(days=6)

    if request.method == "POST":
        form = ShoppingRangeForm(request.POST)
        if form.is_valid():
            build_shopping_list(
                request.user,
                form.cleaned_data["start_date"],
                form.cleaned_data["end_date"],
            )
            messages.success(request, "Wygenerowano nową listę zakupów.")
            return redirect("shopping:shopping_list")
    else:
        form = ShoppingRangeForm(initial={"start_date": today, "end_date": default_end})

    latest_list = ShoppingList.objects.filter(user=request.user).prefetch_related("items").first()
    return render(
        request,
        "shopping/shopping_list.html",
        {"form": form, "shopping_list": latest_list},
    )


@login_required
def toggle_item(request, item_id):
    item = get_object_or_404(ShoppingListItem, id=item_id, shopping_list__user=request.user)
    item.is_checked = not item.is_checked
    item.save(update_fields=["is_checked"])
    return redirect("shopping:shopping_list")
