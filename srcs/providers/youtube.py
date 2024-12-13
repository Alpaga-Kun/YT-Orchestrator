import tempfile
import browser_cookie3
from ..base_soundprovider import BaseSoundProvider
import yt_dlp
import os
import atexit

class YouTubeProvider(BaseSoundProvider):
    provider_name = "youtube"

    def __init__(self):
        try:
            # Crée un fichier temporaire pour stocker les cookies
            self.cookies_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
            self._extract_cookies_to_tempfile()
            atexit.register(self.cleanup_tempfile)  # Assure le nettoyage du fichier temporaire
        except Exception as e:
            raise RuntimeError(f"Initialization failed: {e}")

    def _extract_cookies_to_tempfile(self):
        """Extrait les cookies du navigateur via browser_cookie3 et les écrit dans un fichier temporaire."""
        try:
            cookies = browser_cookie3.chrome()  # Récupère les cookies de Chrome
            with open(self.cookies_tempfile.name, 'w') as f:
                for cookie in cookies:
                    f.write(
                        f"{cookie.domain}\tTRUE\t{cookie.path}\tFALSE\t{cookie.expires}\t{cookie.name}\t{cookie.value}\n"
                    )
        except Exception as e:
            self.cleanup_tempfile()
            raise RuntimeError(f"Failed to extract cookies from browser: {e}")

    def cleanup_tempfile(self):
        """Supprime le fichier temporaire des cookies."""
        try:
            if os.path.exists(self.cookies_tempfile.name):
                os.remove(self.cookies_tempfile.name)
                print(f"Temporary cookie file {self.cookies_tempfile.name} removed.")
        except Exception as e:
            print(f"Error during cleanup of temporary file: {e}")

    def get_playlist_videos(self, playlist_url: str):
        """Récupère les vidéos d'une playlist en utilisant yt_dlp."""
        if not playlist_url or not isinstance(playlist_url, str):
            raise ValueError("Invalid playlist URL provided.")
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # Pour ne pas télécharger les vidéos
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
            if not playlist_info or 'entries' not in playlist_info:
                print(f"Error: No entries found in playlist {playlist_url}")
                raise ValueError("Unable to retrieve playlist videos.")
            return playlist_info.get('entries', [])
        except yt_dlp.DownloadError as e:
            raise RuntimeError(f"Error fetching playlist videos from {playlist_url}: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during playlist retrieval: {e}")

    def download_video(self, video_url: str, output_folder: str) -> None:
        """Télécharge une vidéo spécifique avec des métadonnées."""
        if not video_url or not isinstance(video_url, str):
            raise ValueError("Invalid video URL provided.")
        if not output_folder or not os.path.isdir(output_folder):
            raise ValueError("Invalid output folder provided.")

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
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        except yt_dlp.DownloadError as e:
            raise RuntimeError(f"Failed to download video from {video_url}: {e}")
        except FileNotFoundError as e:
            raise RuntimeError(f"Output folder {output_folder} not found: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during video download: {e}")
