from django.db import models


class SiteConfiguration(models.Model):
    """Global site settings and configuration"""
    site_name = models.CharField(max_length=100, default='RoyalMods')
    site_description = models.TextField(blank=True)
    featured_mods_count = models.PositiveSmallIntegerField(default=5, help_text='Number of featured mods on homepage')
    allow_registrations = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Configuration'
        verbose_name_plural = 'Site Configuration'
    
    def __str__(self):
        return self.site_name
    
    @classmethod
    def getInstance(cls):
        """Get or create singleton site configuration"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class PageTemplate(models.Model):
    """Admin-managed page templates"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title