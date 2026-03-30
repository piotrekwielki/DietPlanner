from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "goal", "daily_calorie_limit", "activity_level")
    search_fields = ("user__username", "user__email")
