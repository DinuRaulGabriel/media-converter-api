"""
URL configuration for media_converte project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

from converter.views import (
    home,
    convert_page,
    my_downloads,
    my_favorites,
    toggle_favorite,
    my_presets,
    delete_preset,
    register,
    logout_view,
    VideoInfo,
    ConvertVideo,
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('convert/', ConvertVideo.as_view(), name='convert_video'),
    path('get_video_info/', VideoInfo.as_view(), name='get_video_info'),
    path('convert-page/', convert_page, name='convert_page'),
    path('login/', LoginView.as_view(template_name='converter/login.html'), name='login'),
    path("register/", register, name="register"),
    path("logout/", logout_view, name="logout"),        
    path('', home, name='home'),
    path("my-downloads/", my_downloads, name="my_downloads"),
    path("my-favorites/", my_favorites, name="my_favorites"),
    path("favorites/toggle/<int:download_id>/", toggle_favorite, name="toggle_favorite"),
    path("my-presets/", my_presets, name="my_presets"),
    path("presets/delete/<int:preset_id>/", delete_preset, name="delete_preset"),
    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Serving media files during development

