from django.db import models
from django.contrib.auth.models import User
from mods.models import Mod


class ModReview(models.Model):
    """Track mod review process"""
    ACTION_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending Review'),
    ]
    
    mod = models.ForeignKey(Mod, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='mod_reviews')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    review_notes = models.TextField(blank=True, help_text='Internal notes for review decision')
    reviewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-reviewed_at']
    
    def __str__(self):
        return f'{self.mod.name} - {self.get_action_display()} by {self.reviewer.username if self.reviewer else "System"}'


class AdminAction(models.Model):
    """Log admin actions for audit trail"""
    ACTION_CHOICES = [
        ('mod_approved', 'Mod Approved'),
        ('mod_rejected', 'Mod Rejected'),
        ('user_banned', 'User Banned'),
        ('user_unbanned', 'User Unbanned'),
        ('game_created', 'Game Created'),
        ('category_created', 'Category Created'),
        ('page_created', 'Page Created'),
        ('other', 'Other Action'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_actions')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_object = models.CharField(max_length=200, help_text='Description of what was acted upon')
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f'{self.get_action_display()} - {self.target_object} by {self.admin_user.username if self.admin_user else "System"}'