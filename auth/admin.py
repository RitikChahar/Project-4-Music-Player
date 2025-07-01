from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

class UserProfileAdmin(UserAdmin):
    model = UserProfile
    list_display = ('username', 'name', 'email', 'is_verified', 'is_active', 'date_created')
    list_filter = ('is_verified', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'name', 'email', 'password')}),
        ('Verification', {'fields': ('is_verified', 'verification_token')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_created')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'name', 'email', 'password1', 'password2',
                'is_staff', 'is_active'
            )
        }),
    )
    search_fields = ('username', 'name', 'email')
    ordering = ('username',)

admin.site.register(UserProfile, UserProfileAdmin)