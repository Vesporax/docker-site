from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomePage.as_view(), name='home'),
    path('featured/', views.FeaturedView.as_view(), name='featured'),
    path('categories/', views.CategoriesView.as_view(), name='categories'),
    path('games/', views.GamesView.as_view(), name='games'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('page/<slug:slug>/', views.PageDetailView.as_view(), name='page_detail'),
]