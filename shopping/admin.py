from django.contrib import admin

from .models import ShoppingList, ShoppingListItem


class ShoppingListItemInline(admin.TabularInline):
    model = ShoppingListItem
    extra = 0


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "start_date", "end_date", "created_at")
    inlines = [ShoppingListItemInline]
