from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..forms import CustomUserCreationForm
from django.contrib.auth import login, logout

from ..filters import DownloadFilter
from ..models import Download, Favorite, ConversionPreset
from .api_views import ConvertVideo


def _index_context(request, **extra):
    """
    Context comun pentru index/home ca sa avem mereu presets disponibili,
    inclusiv dupa convert_page() cand randam iar index.html.
    """
    context = {}

    if request.user.is_authenticated:
        context["presets"] = (
            ConversionPreset.objects
            .filter(user=request.user)
            .order_by("-created_at")
        )
    else:
        context["presets"] = []

    context.update(extra)
    return context


def home(request):
    return render(request, "converter/index.html", _index_context(request))


@login_required
def my_downloads(request):
    base_qs = Download.objects.filter(user=request.user).order_by("-created_at")
    download_filter = DownloadFilter(request.GET, queryset=base_qs)
    filtered_qs = download_filter.qs

    mp3_downloads = filtered_qs.filter(format="mp3")
    mp4_downloads = filtered_qs.filter(format="mp4")

    favorite_ids = set(
        Favorite.objects.filter(user=request.user).values_list("download_id", flat=True)
    )

    return render(
        request,
        "converter/my_downloads.html",
        {
            "filter": download_filter,
            "mp3_downloads": mp3_downloads,
            "mp4_downloads": mp4_downloads,
            "favorite_ids": favorite_ids,
        },
    )


@login_required
def my_favorites(request):
    favorite_download_ids = Favorite.objects.filter(user=request.user).values_list(
        "download_id", flat=True
    )

    base_qs = (
        Download.objects.filter(user=request.user, id__in=favorite_download_ids)
        .order_by("-created_at")
    )

    download_filter = DownloadFilter(request.GET, queryset=base_qs)
    filtered_qs = download_filter.qs

    mp3_downloads = filtered_qs.filter(format="mp3")
    mp4_downloads = filtered_qs.filter(format="mp4")

    return render(
        request,
        "converter/my_favorites.html",
        {
            "filter": download_filter,
            "mp3_downloads": mp3_downloads,
            "mp4_downloads": mp4_downloads,
        },
    )


@login_required
def toggle_favorite(request, download_id):
    if request.method != "POST":
        return redirect("my_downloads")

    download = get_object_or_404(Download, id=download_id, user=request.user)

    favorite = Favorite.objects.filter(user=request.user, download=download).first()
    if favorite:
        favorite.delete()
    else:
        Favorite.objects.create(user=request.user, download=download)

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER")
    return redirect(next_url or "my_downloads")


@login_required
def convert_page(request):
    """
    Web page submit -> foloseste APIView ConvertVideo intern.
    PATCH: toate render-urile catre index.html includ presets prin _index_context().
    """
    if request.method != "POST":
        return render(request, "converter/index.html", _index_context(request))

    url = (request.POST.get("url") or "").strip()
    format_ = (request.POST.get("format") or "").strip()
    quality = (request.POST.get("quality") or "medium").strip()

    if not url or not format_:
        return render(
            request,
            "converter/index.html",
            _index_context(request, error="URL si format sunt obligatorii."),
        )

    try:
        api_view = ConvertVideo()

        # Compatibilitate Django request + DRF APIView
        # (APIView foloseste request.data, dar request normal Django are request.POST)
        request.data = {"url": url, "format": format_, "quality": quality}

        resp = api_view.post(request)

        if resp.status_code != 200:
            return render(
                request,
                "converter/index.html",
                _index_context(
                    request,
                    error=resp.data.get("error", "Eroare necunoscuta"),
                ),
            )

        return render(
            request,
            "converter/index.html",
            _index_context(
                request,
                converted_file_url=resp.data["converted_file_url"],
            ),
        )

    except Exception as e:
        return render(
            request,
            "converter/index.html",
            _index_context(request, error=str(e)),
        )


@login_required
def my_presets(request):
    """
    Pagina pentru creare + listare preseturi.
    """
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        format_ = (request.POST.get("format") or "").strip().lower()
        quality = (request.POST.get("quality") or "").strip().lower()

        if not name or not format_ or not quality:
            presets = ConversionPreset.objects.filter(user=request.user).order_by("-created_at")
            return render(
                request,
                "converter/my_presets.html",
                {
                    "presets": presets,
                    "error": "Completeaza toate campurile.",
                },
            )

        if format_ not in ["mp3", "mp4"]:
            presets = ConversionPreset.objects.filter(user=request.user).order_by("-created_at")
            return render(
                request,
                "converter/my_presets.html",
                {
                    "presets": presets,
                    "error": "Format invalid.",
                },
            )

        if quality not in ["low", "medium", "high"]:
            presets = ConversionPreset.objects.filter(user=request.user).order_by("-created_at")
            return render(
                request,
                "converter/my_presets.html",
                {
                    "presets": presets,
                    "error": "Quality invalid.",
                },
            )

        # optional: evitam duplicate pe acelasi nume/user
        exists = ConversionPreset.objects.filter(user=request.user, name__iexact=name).exists()
        if exists:
            presets = ConversionPreset.objects.filter(user=request.user).order_by("-created_at")
            return render(
                request,
                "converter/my_presets.html",
                {
                    "presets": presets,
                    "error": "Ai deja un preset cu acest nume.",
                },
            )

        ConversionPreset.objects.create(
            user=request.user,
            name=name,
            format=format_,
            quality=quality,
        )
        return redirect("my_presets")

    presets = ConversionPreset.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "converter/my_presets.html", {"presets": presets})


@login_required
def delete_preset(request, preset_id):
    if request.method != "POST":
        return redirect("my_presets")

    preset = get_object_or_404(ConversionPreset, id=preset_id, user=request.user)
    preset.delete()
    return redirect("my_presets")


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="converter.backends.UsernameOrEmailBackend")
            return redirect("home")
    else:
        form = CustomUserCreationForm()

    return render(request, "converter/register.html", {"form": form})



def logout_view(request):
    logout(request)
    return redirect("home")