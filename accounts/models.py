from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class UserProfile(models.Model):
    """Extended user profile for additional information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    self_presentation = models.TextField(blank=True, help_text='Tell others about yourself')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.user.username})


class SocialMediaLink(models.Model):
    """Social media links for user profiles"""
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook/Meta'),
        ('youtube', 'YouTube'),
        ('discord', 'Discord'),
        ('other', 'Other Social Media'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    url = models.URLField()
    display_name = models.CharField(max_length=100, blank=True, help_text='Custom display name for "Other" platforms')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'platform', 'url']
    
    def __str__(self):
        if self.platform == 'other' and self.display_name:
            return f'{self.user.username} - {self.display_name}'
        return f'{self.user.username} - {self.get_platform_display()}'
    
    def get_platform_name(self):
        """Get display name for platform"""
        if self.platform == 'other' and self.display_name:
            return self.display_name
        return self.get_platform_display()