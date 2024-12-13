import tempfile
import browser_cookie3
from ..base_soundprovider import BaseSoundProvider
import yt_dlp

class YouTubeProvider(BaseSoundProvider):
    provider_name = "youtube"

    def __init__(self):
        # Crée un fichier temporaire pour stocker les cookies
        self.cookies_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
        self._extract_cookies_to_tempfile()

    def _extract_cookies_to_tempfile(self):
        """Extrait les cookies du navigateur via browser_cookie3 et les écrit dans un fichier temporaire."""
        try:
            cookies = browser_cookie3.chrome()  # Récupère les cookies de Chrome
            with open(self.cookies_tempfile.name, 'w') as f:
                for cookie in cookies:
                    f.write(f"{cookie.domain}\tTRUE\t{cookie.path}\tFALSE\t{cookie.expires}\t{cookie.name}\t{cookie.value}\n")
        except Exception as e:
            raise RuntimeError(f"Failed to extract cookies from browser: {e}")

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

    def download_video(self, video_url: str, output_folder: str) -> None:
        """Télécharge une vidéo spécifique avec des métadonnées."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                },
                {
                    'key': 'FFmpegMetadata',  # Add metadata (artist, title, etc.)
                },
                {
                    'key': 'EmbedThumbnail',  # Add the thumbnail as cover art
                },
            ],
            'writethumbnail': True,  # Download the video thumbnail
            'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
            'quiet': True,
            'force_overwrites': True,
            'cookies': self.cookies_tempfile.name,  # Utilise le fichier temporaire
            'concurrent_fragment_downloads': 10,
            'http_chunk_size': 16 * 1024 * 1024,  # 16 Mo
            'retries': 3,
            'cachedir': './cache',
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
