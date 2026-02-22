from django.contrib import admin
from .models import Download, Favorite, ConversionPreset

@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "format", "quality", "created_at")
    list_filter = ("format", "quality", "created_at")
    search_fields = ("title", "source_url", "user__username")
    ordering = ("-created_at",)

    readonly_fields = ("created_at","file_path")

    fields = ("user", "title", "source_url", "file_path", "format", "quality", "created_at")

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "download", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "download__title, download__source_url")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


@admin.register(ConversionPreset)
class ConversionPresetAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "format", "quality", "created_at")
    list_filter = ("format", "quality", "created_at")
    search_fields = ("name", "user__username")
    ordering = ("user", "name")
    readonly_fields = ("created_at",)
    