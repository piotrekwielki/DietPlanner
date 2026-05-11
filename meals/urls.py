from django.urls import path

from . import views

app_name = "meals"

urlpatterns = [
    path("", views.meal_list, name="meal_list"),
    path("create/", views.meal_create, name="meal_create"),
    path("<slug:slug>/edit/", views.meal_edit, name="meal_edit"),
    path("<slug:slug>/", views.meal_detail, name="meal_detail"),
    path("<slug:slug>/favorite/", views.toggle_favorite, name="toggle_favorite"),
]
