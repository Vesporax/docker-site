from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db.models import Q
import datetime
from mods.models import Mod, Game, Category
from .models import SiteConfiguration, PageTemplate


class HomePage(ListView):
    """Page d'accueil affichant les mods récents approuvés"""
    model = Mod
    template_name = 'core/home.html'
    context_object_name = 'recent_mods'

    def get_queryset(self):
        config = SiteConfiguration.getInstance()
        return Mod.objects.filter(status='approved').select_related('game', 'main_author')[:config.featured_mods_count]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_config'] = SiteConfiguration.getInstance()
        return context


class FeaturedView(ListView):
    """Page des mods en vedette"""
    model = Mod
    template_name = 'core/featured.html'
    context_object_name = 'featured_mods'
    paginate_by = 12

    def get_queryset(self):
        return Mod.objects.filter(status='approved').select_related('game', 'main_author').order_by('-views_count')


class CategoriesView(ListView):
    """Page de toutes les catégories"""
    model = Category
    template_name = 'core/categories.html'
    context_object_name = 'categories'
    paginate_by = 12

    def get_queryset(self):
        return Category.objects.all().prefetch_related('mods')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for category in context['categories']:
            category.mod_count = category.mods.filter(status='approved').count()
        return context


class GamesView(ListView):
    """Page de tous les jeux"""
    model = Game
    template_name = 'core/games.html'
    context_object_name = 'games'
    paginate_by = 12

    def get_queryset(self):
        return Game.objects.all().prefetch_related('mods')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for game in context['games']:
            game.mod_count = game.mods.filter(status='approved').count()
        return context


class SearchView(ListView):
    """Recherche de mods"""
    model = Mod
    template_name = 'core/search.html'
    context_object_name = 'search_results'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        game_filter = self.request.GET.get('game', '')
        category_filter = self.request.GET.get('category', '')

        queryset = Mod.objects.filter(status='approved').select_related('game', 'main_author')

        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(main_author__username__icontains=query)
            )

        if game_filter:
            queryset = queryset.filter(game__slug=game_filter)

        if category_filter:
            queryset = queryset.filter(categories__slug=category_filter)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['games'] = Game.objects.all()
        context['categories'] = Category.objects.all()
        context['selected_game'] = self.request.GET.get('game', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['total_count'] = self.get_queryset().count()
        return context


class PageDetailView(DetailView):
    """Affiche les pages personnalisées créées par l'admin"""
    model = PageTemplate
    template_name = 'core/page_detail.html'
    context_object_name = 'page'

    def get_queryset(self):
        return PageTemplate.objects.filter(is_active=True)


# ─── Gestionnaires d'erreurs ──────────────────────────────────────────────────

def handler404(request, exception):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    error_info = (
        f"Code d'erreur : 404\n"
        f"URL demandée : {request.path}\n"
        f"Heure : {now}"
    )
    context = {
        'error_code': 404,
        'error_info': error_info,
    }
    return render(request, 'errors/404.html', context, status=404)


def handler500(request):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    error_info = (
        f"Code d'erreur : 500\n"
        f"URL demandée : {request.path}\n"
        f"Heure : {now}"
    )
    context = {
        'error_code': 500,
        'error_info': error_info,
    }
    return render(request, 'errors/500.html', context, status=500)


def handler403(request, exception):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    error_info = (
        f"Code d'erreur : 403\n"
        f"URL demandée : {request.path}\n"
        f"Heure : {now}"
    )
    context = {
        'error_code': 403,
        'error_info': error_info,
    }
    return render(request, 'errors/403.html', context, status=403)