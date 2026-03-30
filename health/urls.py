from django.urls import path

from . import views

app_name = "health"

urlpatterns = [
    path("bmi/", views.bmi_calculator, name="bmi_calculator"),
]
