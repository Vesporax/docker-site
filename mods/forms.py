from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify
from .models import Mod, ModImage, Game, Category


class MultipleFileInput(forms.ClearableFileInput):
    """Custom widget for multiple file uploads"""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Custom field for multiple file uploads"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ModUploadForm(forms.ModelForm):
    """Form for uploading new mods"""
    other_authors = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Select additional authors for this mod'
    )
    
    images = MultipleFileField(
        required=False,
        help_text='Upload up to 6 preview images (PNG or JPG)'
    )
    
    class Meta:
        model = Mod
        fields = ['name', 'description', 'game', 'categories', 'other_authors', 'required_mods', 'version', 'download_link']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'categories': forms.CheckboxSelectMultiple(),
            'required_mods': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['other_authors'].queryset = User.objects.exclude(id=self.instance.main_author_id if self.instance.pk else None)
        self.fields['required_mods'].queryset = Mod.objects.filter(status='approved')
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.name)
        if commit:
            instance.save()
            self.save_m2m()
        return instance