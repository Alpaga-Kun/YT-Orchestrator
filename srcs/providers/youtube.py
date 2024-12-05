from ..base_soundprovider import BaseSoundProvider
import yt_dlp

class YouTubeProvider(BaseSoundProvider):
    provider_name = "youtube"

    def get_playlist_videos(self, playlist_url: str):
        """Récupère les vidéos d'une playlist en utilisant yt_dlp."""
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # Pour ne pas télécharger les vidéos
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
        if 'entries' not in playlist_info:
            raise ValueError("Unable to retrieve playlist videos.")
        return playlist_info['entries']

    def download_video(self, video_url: str, output_folder: str):
        """Télécharge une vidéo spécifique."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
            'quiet': True,  # Désactive la sortie
            'no_warnings': True,  # Supprime les warnings
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

