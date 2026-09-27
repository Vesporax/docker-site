from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, SocialMediaLink


class SocialMediaLinkInline(admin.TabularInline):
    model = SocialMediaLink
    extra = 1


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class CustomUserAdmin(UserAdmin):
    """Extended User admin with profile and social links"""
    inlines = [UserProfileInline, SocialMediaLinkInline]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    list_filter = ['created_at']


@admin.register(SocialMediaLink)
class SocialMediaLinkAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'get_platform_name', 'url', 'created_at']
    list_filter = ['platform', 'created_at']
    search_fields = ['user__username', 'display_name', 'url']


# Unregister default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)