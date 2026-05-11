from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from meals.models import Ingredient, Meal, MealIngredient
from planner.models import PlanTemplate, PlanTemplateMeal


class Command(BaseCommand):
    help = "Tworzy przykladowe dane startowe dla aplikacji dietetycznej."

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("admin12345")
            admin.save()

        user, created = User.objects.get_or_create(
            username="demo",
            defaults={"email": "demo@example.com", "first_name": "Demo"},
        )
        if created:
            user.set_password("demo12345")
            user.save()

        oats = Ingredient.objects.get_or_create(name="Platki owsiane", defaults={"category": "grains"})[0]
        milk = Ingredient.objects.get_or_create(name="Mleko", defaults={"category": "dairy", "default_unit": "ml"})[0]
        banana = Ingredient.objects.get_or_create(name="Banan", defaults={"category": "fruit", "default_unit": "szt."})[0]
        chicken = Ingredient.objects.get_or_create(name="Piers z kurczaka", defaults={"category": "meat"})[0]
        rice = Ingredient.objects.get_or_create(name="Ryz", defaults={"category": "dry"})[0]
        broccoli = Ingredient.objects.get_or_create(name="Brokul", defaults={"category": "vegetables"})[0]
        bread = Ingredient.objects.get_or_create(name="Chleb pelnoziarnisty", defaults={"category": "grains"})[0]
        cottage = Ingredient.objects.get_or_create(name="Serek wiejski", defaults={"category": "dairy"})[0]
        tomato = Ingredient.objects.get_or_create(name="Pomidor", defaults={"category": "vegetables"})[0]

        porridge, _ = Meal.objects.get_or_create(
            name="Owsianka z bananem",
            defaults={
                "description": "Szybkie sniadanie z platkow owsianych, mleka i banana.",
                "calories": 420,
                "protein": 16,
                "fat": 9,
                "carbs": 68,
                "servings": 2,
                "diet_type": "vegetarian",
                "preferred_meal_time": "breakfast",
                "created_by": admin,
                "is_public": True,
                "is_approved": True,
            },
        )
        MealIngredient.objects.get_or_create(meal=porridge, ingredient=oats, defaults={"quantity": 100, "unit": "g"})
        MealIngredient.objects.get_or_create(meal=porridge, ingredient=milk, defaults={"quantity": 300, "unit": "ml"})
        MealIngredient.objects.get_or_create(meal=porridge, ingredient=banana, defaults={"quantity": 2, "unit": "szt."})

        chicken_rice, _ = Meal.objects.get_or_create(
            name="Kurczak z ryzem i brokulem",
            defaults={
                "description": "Klasyczny obiad wysokobialkowy.",
                "calories": 610,
                "protein": 45,
                "fat": 14,
                "carbs": 72,
                "servings": 2,
                "diet_type": "standard",
                "preferred_meal_time": "dinner",
                "created_by": admin,
                "is_public": True,
                "is_approved": True,
            },
        )
        MealIngredient.objects.get_or_create(meal=chicken_rice, ingredient=chicken, defaults={"quantity": 300, "unit": "g"})
        MealIngredient.objects.get_or_create(meal=chicken_rice, ingredient=rice, defaults={"quantity": 160, "unit": "g"})
        MealIngredient.objects.get_or_create(meal=chicken_rice, ingredient=broccoli, defaults={"quantity": 250, "unit": "g"})

        sandwiches, _ = Meal.objects.get_or_create(
            name="Kanapki z serkiem i pomidorem",
            defaults={
                "description": "Lekka kolacja z pieczywem pelnoziarnistym.",
                "calories": 350,
                "protein": 21,
                "fat": 9,
                "carbs": 42,
                "servings": 2,
                "diet_type": "vegetarian",
                "preferred_meal_time": "supper",
                "created_by": admin,
                "is_public": True,
                "is_approved": True,
            },
        )
        MealIngredient.objects.get_or_create(meal=sandwiches, ingredient=bread, defaults={"quantity": 120, "unit": "g"})
        MealIngredient.objects.get_or_create(meal=sandwiches, ingredient=cottage, defaults={"quantity": 200, "unit": "g"})
        MealIngredient.objects.get_or_create(meal=sandwiches, ingredient=tomato, defaults={"quantity": 150, "unit": "g"})

        template, _ = PlanTemplate.objects.get_or_create(
            name="Szablon 2000 kcal",
            defaults={
                "description": "Przykladowy jednodniowy jadlospis o umiarkowanej kalorycznosci.",
                "calorie_target": 2000,
                "is_public": True,
                "created_by": admin,
            },
        )
        PlanTemplateMeal.objects.get_or_create(template=template, meal=porridge, meal_time="breakfast", defaults={"servings": 1})
        PlanTemplateMeal.objects.get_or_create(template=template, meal=chicken_rice, meal_time="dinner", defaults={"servings": 1})
        PlanTemplateMeal.objects.get_or_create(template=template, meal=sandwiches, meal_time="supper", defaults={"servings": 1})

        self.stdout.write(self.style.SUCCESS("Dane startowe zostaly utworzone."))
