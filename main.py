import json
from threading import Thread, Lock
from queue import Queue, Empty
from rich.console import Console
from rich.status import Status
from time import sleep
from typing import List, Dict, Any
import argparse
import os
from srcs import sound_providers
from srcs.utils import Utils

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), './config', '.env'))

class MusicDownloaderApp:
    def __init__(self) -> None:
        """Initialise les attributs de l'application."""
        self.console = Console()
        self.lock = Lock()  # Mutex pour synchroniser l'accès aux téléchargements terminés
        self.completed: List[str] = []  # Liste des vidéos téléchargées avec succès
        self.errors: List[str] = []  # Liste des erreurs rencontrées
        self.AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.CONTAINER_NAME = os.getenv('CONTAINER_NAME')

    # =====================
    #  ARGUMENTS & SETUP
    # =====================

    def parse_arguments(self) -> argparse.Namespace:
        """Configure et parse les arguments de la ligne de commande."""
        parser = argparse.ArgumentParser(description="Music Downloader Application")

        # Choix du provider
        parser.add_argument(
            '--provider',
            type=str,
            required=True,
            choices=sound_providers.keys(),
            help="Specify the sound provider (e.g., youtube, spotify)."
        )

        # Arguments communs
        parser.add_argument(
            '--playlist-url',
            type=str,
            help="URL of a single playlist to process."
        )
        parser.add_argument(
            '--output-folder',
            type=str,
            default="output",
            help="Base folder where the downloaded files will be saved."
        )

        # Chargement d'un fichier JSON
        parser.add_argument(
            '--playlists-json',
            type=str,
            help="Path to a JSON file containing multiple playlists."
        )

        return parser.parse_args()

    def load_playlists_from_json(self, json_path: str) -> List[Dict[str, str]]:
        """Charge les playlists depuis un fichier JSON."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            return data.get("playlists", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.console.print(f"[bold red]Error loading JSON file: {str(e)}[/]")
            return []

    def create_output_folder(self, base_folder: str, playlist_title: str) -> str:
        """Crée un dossier pour une playlist spécifique."""
        playlist_folder = os.path.join(base_folder, playlist_title)
        os.makedirs(playlist_folder, exist_ok=True)
        return playlist_folder

    # =====================
    #  DOWNLOAD MANAGEMENT
    # =====================

    def download_playlist(self, playlist_url: str, output_folder: str, provider: Any) -> None:
        """Télécharge une playlist spécifique."""
        self.console.print(f"[bold cyan]Fetching playlist:[/] {playlist_url}")
        videos = provider.get_playlist_videos(playlist_url)
        self.console.print(f"[bold green]Found {len(videos)} videos in the playlist.[/]")
        self.parallel_download(videos, provider, output_folder)

    def parallel_download(self, videos: List[Dict[str, Any]], provider: Any, output_folder: str) -> None:
        """Téléchargement en parallèle."""
        queue = Queue()
        for video in videos:
            queue.put(video)

        threads = []
        thread_count = min(4, os.cpu_count() or 4)  # Max 4 ou nombre de CPU
        for _ in range(thread_count):
            thread = Thread(target=self.download_worker, args=(queue, provider, output_folder))
            thread.start()
            threads.append(thread)

        with Status("[bold cyan]Downloading videos...[/]", spinner="dots", console=self.console):
            while any(thread.is_alive() for thread in threads):
                # Mutex pour afficher les téléchargements complétés sans conflits
                with self.lock:
                    for title in self.completed:
                        self.console.print(f"[green]Completed:[/] {title}")
                    self.completed.clear()
                sleep(0.5)

        for thread in threads:
            thread.join()

    def download_worker(self, queue: Queue, provider: Any, output_folder: str) -> None:
        """Thread worker pour télécharger les vidéos."""
        while not queue.empty():
            try:
                video = queue.get_nowait()
            except Empty:
                break

            title = video.get("title", "Unknown Title")
            url = video.get("url", video.get("webpage_url"))
            output_path = os.path.join(output_folder, f"{title}.mp3")

            if os.path.exists(output_path):
                self.console.print(f"[yellow]Skipping:[/] {title} (already downloaded)")
                queue.task_done()
                continue

            try:
                provider.download_video(url, output_folder)
                with self.lock:
                    self.completed.append(title)
            except Exception as e:
                with self.lock:
                    self.errors.append(f"{title}: {str(e)}")
            queue.task_done()

    def stock_errors(self) -> None:
        """Affiche les erreurs après les téléchargements."""
        if self.errors:
            self.console.print("[bold red]Errors occurred during downloads:[/]")
            for error in self.errors:
                self.console.print(f"[red]{error}[/]")

    # =====================
    #  APPLICATION ENTRY
    # =====================

    def run(self) -> None:
        """Point d'entrée principal de l'application."""
        # Étape 1 : Parse des arguments
        args = self.parse_arguments()

        # Étape 2 : Vérification du provider
        provider_name = args.provider
        if provider_name not in sound_providers:
            self.console.print(f"[bold red]Provider '{provider_name}' not found. Please check available providers.[/]")
            return

        provider_class = sound_providers[provider_name]
        provider = provider_class()

        # Étape 3 : Initialisation de la classe Utils pour compression et sauvegarde
        utils = Utils(self.AZURE_STORAGE_CONNECTION_STRING, self.CONTAINER_NAME)

        # Étape 4 : Gestion des téléchargements (Playlists JSON ou URL unique)
        if args.playlists_json:
            playlists = self.load_playlists_from_json(args.playlists_json)
            for playlist in playlists:
                title = playlist["title"]
                url = playlist["url"]

                # Création du dossier pour chaque playlist
                playlist_folder = self.create_output_folder(args.output_folder, title)
                self.download_playlist(url, playlist_folder, provider)
        elif args.playlist_url:
            # Télécharger une playlist unique
            playlist_folder = self.create_output_folder(args.output_folder, "single_playlist")
            self.download_playlist(args.playlist_url, playlist_folder, provider)
        else:
            self.console.print("[bold red]Error: You must provide either --playlist-url or --playlists-json[/]")
            return

        # Étape 5 : Compression des fichiers téléchargés
        try:
            self.console.print("[bold cyan]Compressing downloaded files...[/]")
            zip_file = utils.compress_folder(args.output_folder, "compressed_music.zip")

            # Étape 6 : Upload vers OneDrive (via Azure Blob Storage)
            self.console.print("[bold cyan]Uploading compressed file to Azure Blob Storage...[/]")
            link = utils.upload_to_blob_storage(zip_file)
            self.console.print(f"[bold green]Uploaded successfully. Access it here: {link}[/]")

            # Étape 7 : Nettoyage local des fichiers compressés
            self.console.print("[bold yellow]Cleaning up local files...[/]")
            utils.cleanup([zip_file])

        except Exception as e:
            self.console.print(f"[bold red]An error occurred during post-processing: {str(e)}[/]")

        # Étape 8 : Affichage des erreurs de téléchargement, s'il y en a
        self.stock_errors()


if __name__ == "__main__":
    app = MusicDownloaderApp()
    app.run()
