from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/<str:username>/', views.UserProfileView.as_view(), name='profile'),
    path('settings/', views.UserSettingsView.as_view(), name='settings'),
    path('creator-studio/', views.CreatorStudioView.as_view(), name='creator_studio'),
]