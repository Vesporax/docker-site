from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from .models import UserProfile
from .forms import UserProfileForm
from mods.models import Mod


class UserProfileView(DetailView):
    """Page de profil public d'un utilisateur"""
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['user_mods'] = Mod.objects.filter(
            main_author=user,
            status='approved'
        ).select_related('game').prefetch_related('categories')[:6]
        context['social_links'] = user.social_links.all()
        return context


class UserSettingsView(LoginRequiredMixin, UpdateView):
    """Page de paramètres pour modifier le profil"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/settings.html'
    success_url = reverse_lazy('accounts:settings')

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Profil mis à jour avec succès !')
        return response


class CreatorStudioView(LoginRequiredMixin, ListView):
    """Tableau de bord du créateur"""
    model = Mod
    template_name = 'accounts/creator_studio.html'
    context_object_name = 'user_mods'
    paginate_by = 12

    def get_queryset(self):
        return Mod.objects.filter(main_author=self.request.user).select_related('game').prefetch_related('categories').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_mods = self.get_queryset()
        context['pending_count'] = user_mods.filter(status='pending').count()
        context['approved_count'] = user_mods.filter(status='approved').count()
        context['rejected_count'] = user_mods.filter(status='rejected').count()
        return context