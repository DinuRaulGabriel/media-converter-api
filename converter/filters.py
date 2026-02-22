import django_filters
from django import forms
from .models import Download

class DownloadFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        label="Search title",
        widget=forms.TextInput(attrs={"placeholder": "Type part of title..."})
    )

    format = django_filters.ChoiceFilter(
        field_name="format",
        choices=[("mp3", "mp3"), ("mp4", "mp4")],
        label="Format",
        empty_label="Any"
    )

    quality = django_filters.ChoiceFilter(
        field_name="quality",
        choices=[("low", "low"), ("medium", "medium"), ("high", "high")],
        label="Quality",
        empty_label="Any"
    )

    created_after = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__gte",
        label="From date",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    created_before = django_filters.DateFilter(
        field_name="created_at",
        lookup_expr="date__lte",
        label="To date",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    class Meta:
        model = Download
        fields = ["title", "format", "quality", "created_after", "created_before"]