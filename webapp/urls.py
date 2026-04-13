from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('settings/', views.settings_view, name='settings'),
    path('video/<int:video_id>/stream/', views.video_stream, name='video_stream'),
    path('video/<int:video_id>/progress/', views.update_progress, name='update_progress'),
]
