from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image
import os


def gameIconPath(instance, filename):
    """Generate upload path for game icons"""
    ext = filename.split('.')[-1]
    return f'games/icons/{instance.slug}.{ext}'


def gameBannerPath(instance, filename):
    """Generate upload path for game banners"""
    ext = filename.split('.')[-1]
    return f'games/banners/{instance.slug}.{ext}'


def categoryIconPath(instance, filename):
    """Generate upload path for category icons"""
    ext = filename.split('.')[-1]
    return f'categories/icons/{instance.slug}.{ext}'


def categoryBannerPath(instance, filename):
    """Generate upload path for category banners"""
    ext = filename.split('.')[-1]
    return f'categories/banners/{instance.slug}.{ext}'


class Game(models.Model):
    """Admin-managed game supercategories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.ImageField(upload_to=gameIconPath, blank=True, null=True)
    banner = models.ImageField(upload_to=gameBannerPath, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize icon to 120x120 max
        if self.icon:
            img = Image.open(self.icon.path)
            if img.width > 120 or img.height > 120:
                img.thumbnail((120, 120), Image.LANCZOS)
                img.save(self.icon.path, optimize=True, quality=85)
        
        # Resize banner to 16:9 ratio with 800px max width
        if self.banner:
            img = Image.open(self.banner.path)
            maxWidth = 800
            targetRatio = 16/9
            
            if img.width > maxWidth:
                newWidth = maxWidth
                newHeight = int(newWidth / targetRatio)
            else:
                newWidth = img.width
                newHeight = int(newWidth / targetRatio)
            
            img = img.resize((newWidth, newHeight), Image.LANCZOS)
            img.save(self.banner.path, optimize=True, quality=85)


class Category(models.Model):
    """Admin-managed categories for mod classification"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to=categoryIconPath, blank=True, null=True)
    banner = models.ImageField(upload_to=categoryBannerPath, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize icon to 120x120 max
        if self.icon:
            img = Image.open(self.icon.path)
            if img.width > 120 or img.height > 120:
                img.thumbnail((120, 120), Image.LANCZOS)
                img.save(self.icon.path, optimize=True, quality=85)
        
        # Resize banner to 16:9 ratio with 800px max width
        if self.banner:
            img = Image.open(self.banner.path)
            maxWidth = 800
            targetRatio = 16/9
            
            if img.width > maxWidth:
                newWidth = maxWidth
                newHeight = int(newWidth / targetRatio)
            else:
                newWidth = img.width
                newHeight = int(newWidth / targetRatio)
            
            img = img.resize((newWidth, newHeight), Image.LANCZOS)
            img.save(self.banner.path, optimize=True, quality=85)


class Mod(models.Model):
    """Main mod model"""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='mods')
    categories = models.ManyToManyField(Category, related_name='mods')
    main_author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_mods')
    other_authors = models.ManyToManyField(User, blank=True, related_name='coauthored_mods')
    required_mods = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='dependent_mods')
    version = models.CharField(max_length=50)
    download_link = models.URLField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    views_count = models.PositiveIntegerField(default=0)
    downloads_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('mods:detail', kwargs={'slug': self.slug})
    
    def increment_views(self):
        """Increment view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_downloads(self):
        """Increment download count"""
        self.downloads_count += 1
        self.save(update_fields=['downloads_count'])


def modImagePath(instance, filename):
    """Generate upload path for mod images"""
    return f'mods/{instance.mod.slug}/images/{filename}'


class ModImage(models.Model):
    """Mod preview images - up to 6 per mod"""
    mod = models.ForeignKey(Mod, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=modImagePath)
    order = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['mod', 'order']
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image to 16:9 ratio with 800px max width
        img = Image.open(self.image.path)
        
        # Calculate 16:9 dimensions
        maxWidth = 800
        targetRatio = 16/9
        
        if img.width > maxWidth:
            newWidth = maxWidth
            newHeight = int(newWidth / targetRatio)
        else:
            newWidth = img.width
            newHeight = int(newWidth / targetRatio)
        
        # Resize and save
        img = img.resize((newWidth, newHeight), Image.LANCZOS)
        img.save(self.image.path, optimize=True, quality=85)
    
    def __str__(self):
        return f'{self.mod.name} - Image {self.order + 1}'