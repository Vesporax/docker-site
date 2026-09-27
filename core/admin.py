from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import SiteConfiguration, PageTemplate


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'allow_registrations', 'maintenance_mode', 'updated_at']
    fieldsets = [
        ('General Settings', {
            'fields': ('site_name', 'site_description', 'featured_mods_count')
        }),
        ('Access Control', {
            'fields': ('allow_registrations', 'maintenance_mode', 'maintenance_message')
        }),
    ]

    def has_add_permission(self, request):
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PageTemplate)
class PageTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_active', 'updated_at']
    list_filter = ['is_active']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']

    # Agrandir la zone de texte du contenu
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={
                'rows': 30,
                'style': 'font-family: monospace; font-size: 14px;',
            })
        },
    }

    fieldsets = [
        ('Informations de la page', {
            'fields': ('title', 'slug', 'is_active'),
        }),
        ('Contenu', {
            'fields': ('content',),
            'description': (
                '<div style="background:#fffbe6;border:1px solid #ffe58f;padding:12px;margin-bottom:12px;border-radius:4px;color:#000000">'
                '<strong>📝 Instructions pour rédiger le contenu :</strong><br><br>'
                '• Écrivez en <strong>texte brut</strong> — pas besoin de HTML.<br>'
                '• Pour créer un <strong>paragraphe</strong>, laissez une ligne vide entre deux blocs de texte.<br>'
                '• Pour un <strong>simple retour à la ligne</strong>, appuyez une fois sur Entrée.<br>'
                '• Exemple de structure :<br>'
                '<pre style="background:#f5f5f5;padding:8px;margin-top:6px;">'
                'Titre de section\n\nPremier paragraphe du texte.\n\nDeuxième paragraphe.'
                '</pre>'
                '</div>'
            ),
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    ]

    actions = ['activate_pages', 'deactivate_pages']

    def activate_pages(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} page(s) activated successfully.')
    activate_pages.short_description = 'Activate selected pages'

    def deactivate_pages(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} page(s) deactivated.')
    deactivate_pages.short_description = 'Deactivate selected pages'