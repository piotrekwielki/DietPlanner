from django.urls import path

from . import views

app_name = "shopping"

urlpatterns = [
    path("", views.shopping_list_view, name="shopping_list"),
    path("toggle/<int:item_id>/", views.toggle_item, name="toggle_item"),
]
