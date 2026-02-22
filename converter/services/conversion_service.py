import os
import uuid

import ffmpeg
import yt_dlp

from django.utils.text import slugify

from ..models import Download


def download_video(url, base_name, output_format):
    downloads_dir = os.path.join("media", "downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    outtmpl = os.path.join(downloads_dir, f"{base_name}.%(ext)s")

    if output_format in ["mp4", "avi", "mov"]:
        ydl_format = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    else:
        ydl_format = "bestaudio/best"

    ydl_opts = {
        "format": ydl_format,
        "outtmpl": outtmpl,
        "noplaylist": True,
        "no_color": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        real_path = ydl.prepare_filename(info)

    return real_path


def perform_conversion(request, url, output_format, quality):
    """
    Logica de conversie comuna pentru:
    - API (DRF)
    - Pagina HTML (Django)
    Returneaza: {"converted_file_url": "..."}
    Ridica ValueError / Exception in caz de eroare.
    """
    url = (url or "").strip()
    output_format = (output_format or "").strip().lower()
    quality = (quality or "medium").strip().lower()

    if not url or not output_format:
        raise ValueError("All fields are required")

    video_bitrates = {
        "low": "1000k",
        "medium": "1500k",
        "high": "3000k",
    }

    audio_bitrates = {
        "low": "128k",
        "medium": "180k",
        "high": "320k",
    }

    if quality not in ("low", "medium", "high"):
        quality = "medium"

    vbr = video_bitrates[quality]
    abr = audio_bitrates[quality]

    # 1) extrage info
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(url, download=False)
        title = info.get("title", "Unknown Title")
    except Exception as e:
        raise Exception(f"Error extracting video: {str(e)}")

    sanitized_title = slugify(title) or "video"

    # nume unic pentru output (evita overwrite)
    output_unique = uuid.uuid4().hex[:8]
    output_filename = f"{sanitized_title}-{output_unique}.{output_format}"
    output_path = os.path.join("media", "converted", output_filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # nume unic pentru fisierul temporar descarcat
    temp_base_name = f"{sanitized_title}-{uuid.uuid4().hex[:8]}"

    # 2) descarca
    try:
        input_path = download_video(url, temp_base_name, output_format)
    except Exception as e:
        raise Exception(f"Error downloading video: {str(e)}")

    if not os.path.exists(input_path):
        raise Exception(f"Downloaded file not found: {input_path}")

    # 3) converteste
    try:
        if output_format in ["mp4", "mov", "avi"]:
            ffmpeg.input(input_path).output(
                output_path,
                video_bitrate=vbr,
                audio_bitrate=abr,
            ).run(overwrite_output=True)

        elif output_format == "mp3":
            ffmpeg.input(input_path).output(
                output_path,
                audio_bitrate=abr,
            ).run(overwrite_output=True)

        else:
            raise ValueError("Unsupported format")

    except ffmpeg.Error as e:
        error_message = (
            e.stderr.decode(errors="ignore")
            if getattr(e, "stderr", None)
            else "Error decoding"
        )
        raise Exception(f"Failed to convert video: {error_message}")

    finally:
        # sterge fisierul temporar descarcat
        if "input_path" in locals() and os.path.exists(input_path):
            os.remove(input_path)

    converted_file_url = request.build_absolute_uri(f"/media/converted/{output_filename}")

    # salveaza in DB daca userul e logat
    if getattr(request, "user", None) and request.user.is_authenticated and output_format in ["mp3", "mp4"]:
        Download.objects.create(
            user=request.user,
            title=title,
            source_url=url,
            file_path=output_path,  # ex: media/converted/video-abc123.mp3
            format=output_format,
            quality=quality,
        )

    return {"converted_file_url": converted_file_url}