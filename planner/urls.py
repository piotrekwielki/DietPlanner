from django.urls import path

from . import views

app_name = "planner"

urlpatterns = [
    path("", views.weekly_planner, name="weekly_planner"),
    path("day/<str:day>/", views.day_detail, name="day_detail"),
    path("copy/", views.copy_day_plan, name="copy_day_plan"),
    path("apply-template/", views.apply_template, name="apply_template"),
    path("remove/<int:planned_meal_id>/", views.remove_planned_meal, name="remove_planned_meal"),
]
