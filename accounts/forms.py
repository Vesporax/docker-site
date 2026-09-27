from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from .models import UserProfile, SocialMediaLink


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Optional'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Optional'})
    )
    
    # Individual social media fields
    facebook_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://facebook.com/yourprofile'})
    )
    youtube_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://youtube.com/@yourchannel'})
    )
    discord_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://discord.gg/yourserver'})
    )
    other_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'Any other social media URL'})
    )
    other_display_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Display name for other social media'})
    )
    
    class Meta:
        model = UserProfile
        fields = ['self_presentation']
        widgets = {
            'self_presentation': forms.Textarea(attrs={
                'rows': 6, 
                'class': 'form-input',
                'placeholder': 'Tell others about yourself, your interests, and what kind of mods you create...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            user = self.instance.user
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            
            # Load existing social links
            social_links = user.social_links.all()
            for link in social_links:
                if link.platform == 'facebook':
                    self.fields['facebook_url'].initial = link.url
                elif link.platform == 'youtube':
                    self.fields['youtube_url'].initial = link.url
                elif link.platform == 'discord':
                    self.fields['discord_url'].initial = link.url
                elif link.platform == 'other':
                    self.fields['other_url'].initial = link.url
                    self.fields['other_display_name'].initial = link.display_name
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            user = profile.user
            user.username = self.cleaned_data['username']
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.save()
            profile.save()
            
            # Handle social media links
            user.social_links.all().delete()  # Clear existing links
            
            if self.cleaned_data['facebook_url']:
                SocialMediaLink.objects.create(
                    user=user,
                    platform='facebook',
                    url=self.cleaned_data['facebook_url']
                )
            
            if self.cleaned_data['youtube_url']:
                SocialMediaLink.objects.create(
                    user=user,
                    platform='youtube',
                    url=self.cleaned_data['youtube_url']
                )
            
            if self.cleaned_data['discord_url']:
                SocialMediaLink.objects.create(
                    user=user,
                    platform='discord',
                    url=self.cleaned_data['discord_url']
                )
            
            if self.cleaned_data['other_url']:
                SocialMediaLink.objects.create(
                    user=user,
                    platform='other',
                    url=self.cleaned_data['other_url'],
                    display_name=self.cleaned_data.get('other_display_name', '')
                )
        
        return profile