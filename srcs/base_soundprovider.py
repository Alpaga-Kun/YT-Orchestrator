from abc import ABC, abstractmethod

class BaseSoundProvider(ABC):
    """
    Classe abstraite pour les fournisseurs de musique.
    Tous les fournisseurs doivent implémenter ces méthodes.
    """
    provider_name = None  # Nom unique du fournisseur (ex. 'youtube', 'spotify')

    @abstractmethod
    def get_playlist_videos(self, playlist_url: str):
        """Récupère les vidéos d'une playlist."""
        pass

    @abstractmethod
    def download_video(self, video_url: str, output_folder: str):
        """Télécharge une vidéo spécifique."""
        pass
