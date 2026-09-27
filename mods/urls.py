from django.urls import path
from . import views

app_name = 'mods'

urlpatterns = [
    path('', views.ModListView.as_view(), name='list'),
    path('upload/', views.ModUploadView.as_view(), name='upload'),
    path('game/<slug:game_slug>/', views.GameModsView.as_view(), name='by_game'),
    path('category/<slug:category_slug>/', views.CategoryModsView.as_view(), name='by_category'),
    path('<slug:slug>/edit/', views.ModEditView.as_view(), name='edit'),
    path('<slug:slug>/download/', views.ModDownloadView.as_view(), name='download'),
    path('<slug:slug>/', views.ModDetailView.as_view(), name='detail'),
]