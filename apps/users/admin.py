from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin

from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = (*BaseUserAdmin.list_display, 'avatar')
    fieldsets = (
        *BaseUserAdmin.fieldsets,
        ('Avatar', {'fields': ('avatar',)}),
    )
    add_fieldsets = (
        *BaseUserAdmin.add_fieldsets,
        ('Personal info', {'fields': ('email', 'avatar')}),
    )
