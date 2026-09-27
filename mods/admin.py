from django.contrib import admin
from .models import Game, Category, Mod, ModImage


class ModImageInline(admin.TabularInline):
    model = ModImage
    extra = 1
    max_num = 6


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'has_icon', 'has_banner', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    fields = ['name', 'slug', 'icon', 'banner']
    
    def has_icon(self, obj):
        return bool(obj.icon)
    has_icon.boolean = True
    has_icon.short_description = 'Icon'
    
    def has_banner(self, obj):
        return bool(obj.banner)
    has_banner.boolean = True
    has_banner.short_description = 'Banner'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'has_icon', 'has_banner', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    fields = ['name', 'slug', 'description', 'icon', 'banner']
    
    def has_icon(self, obj):
        return bool(obj.icon)
    has_icon.boolean = True
    has_icon.short_description = 'Icon'
    
    def has_banner(self, obj):
        return bool(obj.banner)
    has_banner.boolean = True
    has_banner.short_description = 'Banner'


@admin.register(Mod)
class ModAdmin(admin.ModelAdmin):
    list_display = ['name', 'game', 'main_author', 'status', 'views_count', 'downloads_count', 'created_at']
    list_filter = ['status', 'game', 'categories', 'created_at']
    search_fields = ['name', 'description', 'main_author__username']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['categories', 'other_authors', 'required_mods']
    inlines = [ModImageInline]
    
    actions = ['approve_mods', 'reject_mods']
    
    def approve_mods(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} mods approved successfully.')
    approve_mods.short_description = 'Approve selected mods'
    
    def reject_mods(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} mods rejected.')
    reject_mods.short_description = 'Reject selected mods'