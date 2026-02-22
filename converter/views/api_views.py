import yt_dlp

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..services.conversion_service import perform_conversion


class VideoInfo(APIView):
    def post(self, request, *args, **kwargs):
        data = getattr(request, "data", request.POST)
        url = (data.get("url") or "").strip()

        if not url:
            return Response(
                {"error": "No URL provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)

            video_info = {
                "title": info.get("title", "Unknown Title"),
                "duration": info.get("duration", "Unknown Duration"),
                "thumbnail": info.get("thumbnail", ""),
            }
            return Response(video_info, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConvertVideo(APIView):
    def post(self, request, *args, **kwargs):
        data = getattr(request, "data", request.POST)

        url = (data.get("url") or "").strip()
        output_format = (data.get("format") or "").strip().lower()
        quality = (data.get("quality") or "medium").strip().lower()

        try:
            result = perform_conversion(request, url, output_format, quality)
            return Response(result, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )