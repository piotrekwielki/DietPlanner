from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import MealForm, MealIngredientFormSet
from .models import FavoriteMeal, Meal


def visible_meals(user):
    if user.is_authenticated:
        return Meal.objects.filter(Q(is_public=True, is_approved=True) | Q(created_by=user))
    return Meal.objects.filter(is_public=True, is_approved=True)


def meal_list(request):
    meals = visible_meals(request.user).select_related("created_by")

    query = request.GET.get("query", "").strip()
    diet_type = request.GET.get("diet_type", "").strip()
    max_calories = request.GET.get("max_calories", "").strip()

    if query:
        meals = meals.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if diet_type:
        meals = meals.filter(diet_type=diet_type)
    if max_calories:
        meals = meals.filter(calories__lte=max_calories)

    favorite_ids = set()
    if request.user.is_authenticated:
        favorite_ids = set(
            FavoriteMeal.objects.filter(user=request.user, meal__in=meals).values_list(
                "meal_id", flat=True
            )
        )

    return render(
        request,
        "meals/meal_list.html",
        {
            "meals": meals,
            "favorite_ids": favorite_ids,
            "filters": {
                "query": query,
                "diet_type": diet_type,
                "max_calories": max_calories,
            },
            "diet_choices": Meal.DIET_CHOICES,
        },
    )


def meal_detail(request, slug):
    meal = get_object_or_404(
        visible_meals(request.user).prefetch_related("meal_ingredients__ingredient"),
        slug=slug,
    )
    is_favorite = (
        request.user.is_authenticated
        and FavoriteMeal.objects.filter(user=request.user, meal=meal).exists()
    )
    return render(
        request,
        "meals/meal_detail.html",
        {"meal": meal, "is_favorite": is_favorite, "today": timezone.localdate()},
    )


@login_required
def meal_create(request):
    if request.method == "POST":
        form = MealForm(request.POST)
        formset = MealIngredientFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            meal = form.save(commit=False)
            meal.created_by = request.user
            meal.is_approved = request.user.is_staff
            meal.save()
            formset.instance = meal
            formset.save()
            messages.success(request, "Danie zostało dodane.")
            return redirect("meals:meal_detail", slug=meal.slug)
    else:
        form = MealForm()
        formset = MealIngredientFormSet()

    return render(request, "meals/meal_form.html", {"form": form, "formset": formset})


@login_required
def meal_edit(request, slug):
    meal = get_object_or_404(visible_meals(request.user), slug=slug)

    if request.method == "POST":
        form = MealForm(request.POST, instance=meal)
        formset = MealIngredientFormSet(request.POST, instance=meal)
        if form.is_valid() and formset.is_valid():
            meal = form.save(commit=False)
            meal.save()
            formset.save()
            messages.success(request, "Danie zostało zaktualizowane.")
            return redirect("meals:meal_detail", slug=meal.slug)
    else:
        form = MealForm(instance=meal)
        formset = MealIngredientFormSet(instance=meal)

    return render(
        request,
        "meals/meal_form.html",
        {"form": form, "formset": formset, "meal": meal, "is_edit": True},
    )


@login_required
def toggle_favorite(request, slug):
    meal = get_object_or_404(visible_meals(request.user), slug=slug)
    favorite, created = FavoriteMeal.objects.get_or_create(user=request.user, meal=meal)
    if not created:
        favorite.delete()
        messages.info(request, "Danie usunięto z ulubionych.")
    else:
        messages.success(request, "Danie dodano do ulubionych.")
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    return redirect("meals:meal_detail", slug=meal.slug)
