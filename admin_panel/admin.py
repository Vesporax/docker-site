from django.contrib import admin
from .models import ModReview, AdminAction


@admin.register(ModReview)
class ModReviewAdmin(admin.ModelAdmin):
    list_display = ['mod', 'reviewer', 'action', 'reviewed_at']
    list_filter = ['action', 'reviewed_at']
    search_fields = ['mod__name', 'reviewer__username', 'review_notes']
    readonly_fields = ['reviewed_at']
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of review records for audit trail"""
        return False


@admin.register(AdminAction)
class AdminActionAdmin(admin.ModelAdmin):
    list_display = ['action', 'target_object', 'admin_user', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['target_object', 'admin_user__username', 'details']
    readonly_fields = ['timestamp']
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of admin action logs for audit trail"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Make admin actions read-only after creation"""
        return False