# downloader/views.py
import os
import uuid
from django.http import FileResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import yt_dlp

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


@api_view(['GET'])
def health(request):
    return Response({"status": "ok"})


@api_view(['GET'])
def video_info(request):
    url = request.query_params.get("url")
    if not url:
        return Response({"error": "Missing URL"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)

            formats = [
                {
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "resolution": f.get("format_note") or f.get("height"),
                    "filesize": f.get("filesize")
                }
                for f in info.get("formats", [])
                if f.get("filesize") is not None
            ]

            return Response({
                "title": info.get("title"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "uploader": info.get("uploader"),
                "formats": formats
            })

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def download_video(request):
    url = request.query_params.get("url")
    if not url:
        return Response({"error": "Missing URL"}, status=status.HTTP_400_BAD_REQUEST)

    temp_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, f"{temp_id}.%(ext)s")

    ydl_opts = {
        'outtmpl': output_template,
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not filename.endswith(".mp4"):
                filename = os.path.splitext(filename)[0] + ".mp4"

            if not os.path.exists(filename):
                return Response({"error": "Erro ao baixar o vídeo"}, status=500)

    except Exception as e:
        return Response({"error": str(e)}, status=400)

    return FileResponse(open(filename, 'rb'), as_attachment=True, filename=os.path.basename(filename))
