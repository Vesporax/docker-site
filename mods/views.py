from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from .models import Mod, ModImage, Game, Category
from .forms import ModUploadForm


class ModListView(ListView):
    """Liste de tous les mods approuvés"""
    model = Mod
    template_name = 'mods/list.html'
    context_object_name = 'mods'
    paginate_by = 12

    def get_queryset(self):
        qs = Mod.objects.filter(status='approved').select_related('game', 'main_author').prefetch_related('categories')
        author = self.request.GET.get('author', '')
        if author:
            qs = qs.filter(main_author__username=author)
        return qs


class ModDetailView(DetailView):
    """Page individuelle d'un mod"""
    model = Mod
    template_name = 'mods/detail.html'
    context_object_name = 'mod'

    def get_queryset(self):
        return Mod.objects.filter(status='approved').select_related('game', 'main_author').prefetch_related('categories', 'other_authors', 'images', 'required_mods')

    def get_object(self):
        obj = super().get_object()
        obj.increment_views()
        return obj


class GameModsView(ListView):
    """Mods filtrés par jeu"""
    model = Mod
    template_name = 'mods/by_game.html'
    context_object_name = 'mods'
    paginate_by = 12

    def get_queryset(self):
        gameSlug = self.kwargs['game_slug']
        return Mod.objects.filter(status='approved', game__slug=gameSlug).select_related('game', 'main_author').prefetch_related('categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = get_object_or_404(Game, slug=self.kwargs['game_slug'])
        return context


class CategoryModsView(ListView):
    """Mods filtrés par catégorie"""
    model = Mod
    template_name = 'mods/by_category.html'
    context_object_name = 'mods'
    paginate_by = 12

    def get_queryset(self):
        categorySlug = self.kwargs['category_slug']
        return Mod.objects.filter(status='approved', categories__slug=categorySlug).select_related('game', 'main_author').prefetch_related('categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        return context


class ModUploadView(LoginRequiredMixin, CreateView):
    """Formulaire d'envoi d'un nouveau mod"""
    model = Mod
    form_class = ModUploadForm
    template_name = 'mods/upload.html'
    success_url = reverse_lazy('accounts:creator_studio')

    def form_valid(self, form):
        form.instance.main_author = self.request.user
        response = super().form_valid(form)

        images = self.request.FILES.getlist('images')
        for i, image_file in enumerate(images[:6]):
            ModImage.objects.create(
                mod=form.instance,
                image=image_file,
                order=i
            )

        messages.success(self.request, 'Mod téléversé avec succès ! Il sera examiné par un administrateur avant d\'être publié.')
        return response


class ModDownloadView(View):
    """Incrémente le compteur de téléchargements et redirige"""
    def get(self, request, slug):
        mod = get_object_or_404(Mod, slug=slug, status='approved')
        mod.increment_downloads()
        return redirect(mod.download_link)


class ModEditView(LoginRequiredMixin, UpdateView):
    """Modification d'un mod existant (auteur principal uniquement)"""
    model = Mod
    form_class = ModUploadForm
    template_name = 'mods/edit.html'
    success_url = reverse_lazy('accounts:creator_studio')
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.main_author != self.request.user:
            raise PermissionDenied
        return obj

    def form_valid(self, form):
        # Si de nouvelles images sont uploadées, remplacer les anciennes
        images = self.request.FILES.getlist('images')
        response = super().form_valid(form)

        if images:
            self.object.images.all().delete()
            for i, image_file in enumerate(images[:6]):
                ModImage.objects.create(
                    mod=self.object,
                    image=image_file,
                    order=i
                )

        # Repasser en pending si le mod était approuvé
        if self.object.status == 'approved':
            self.object.status = 'pending'
            self.object.save(update_fields=['status'])

        messages.success(self.request, 'Mod mis à jour avec succès ! Il devra être réexaminé avant d\'être republié.')
        return response