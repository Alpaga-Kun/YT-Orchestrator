from threading import Thread, Lock
from queue import Queue, Empty
from rich.console import Console
from rich.status import Status
from time import sleep
from typing import List, Dict, Any
import argparse
import os
from srcs import sound_providers

class MusicDownloaderApp:
    def __init__(self) -> None:
        self.console = Console()
        self.lock = Lock()  # Mutex pour synchroniser l'accès aux téléchargements terminés
        self.completed: List[str] = []  # Liste des vidéos téléchargées avec succès
        self.errors: List[str] = []  # Liste des erreurs rencontrées

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
            required=True,
            help="URL of the playlist to process."
        )
        parser.add_argument(
            '--output-folder',
            type=str,
            default="output",
            help="Folder where the downloaded files will be saved."
        )

        # Arguments spécifiques au provider
        parser.add_argument(
            '--extra-option',
            type=str,
            help="Additional options specific to the provider (optional)."
        )

        return parser.parse_args()

    def download_worker(self, queue: Queue, provider: Any, output_folder: str) -> None:
        """Thread worker pour télécharger les vidéos avec gestion des interruptions."""
        while not queue.empty():
            try:
                video = queue.get_nowait()
            except Empty:
                break  # Si la queue est vide, on sort

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

    def parallel_download(self, videos: List[Dict[str, Any]], provider: Any, output_folder: str) -> None:
        """
        Gère les téléchargements parallèles avec threads et affiche les téléchargements terminés.
        """
        queue = Queue()
        for video in videos:
            queue.put(video)

        # Créer des threads
        threads = []
        thread_count = min(4, os.cpu_count() or 4)  # Max 4 ou nombre de CPU
        for _ in range(thread_count):
            thread = Thread(target=self.download_worker, args=(queue, provider, output_folder))
            thread.start()
            threads.append(thread)

        # Afficher le statut global des téléchargements
        with Status("[bold cyan]Downloading videos...[/]", spinner="dots", console=self.console):
            try:
                while any(thread.is_alive() for thread in threads):
                    # Mutex pour afficher les téléchargements complétés sans conflits
                    with self.lock:
                        for title in self.completed:
                            self.console.print(f"[green]Completed:[/] {title}")
                        self.completed.clear()  # Vider la liste pour ne pas réafficher les mêmes vidéos
                    sleep(0.5)  # Pause pour éviter une surcharge de l'affichage
            except KeyboardInterrupt:
                self.console.print("[bold red]Download interrupted by user![/]")
                for thread in threads:
                    thread.join(timeout=1)
                return

        # Attendre la fin de tous les threads
        for thread in threads:
            thread.join()

    def stock_errors(self) -> None:
        """Affiche les erreurs après les téléchargements."""
        if self.errors:
            self.console.print("[bold red]Errors occurred during downloads:[/]")
            for error in self.errors:
                self.console.print(f"[red]{error}[/]")

    def run(self) -> None:
        """Point d'entrée principal de l'application."""
        args = self.parse_arguments()

        # Charger le provider
        provider_name = args.provider
        if provider_name in sound_providers:
            provider_class = sound_providers[provider_name]
            provider = provider_class()

            # Traitement des playlists
            self.console.print(f"[bold cyan]Using provider:[/] {provider_name}")
            self.console.print(f"[bold cyan]Fetching playlist:[/] {args.playlist_url}")

            videos = provider.get_playlist_videos(args.playlist_url)
            self.console.print(f"[bold green]Found {len(videos)} videos in the playlist.[/]")

            # Lancer les téléchargements parallèles
            self.parallel_download(videos, provider, args.output_folder)

            # Afficher les erreurs si nécessaire
            self.stock_errors()

            self.console.print(f"[bold green]All files have been downloaded to: {args.output_folder}[/]")
        else:
            self.console.print(f"[bold red]Provider '{provider_name}' not found. Please check available providers.[/]")

if __name__ == "__main__":
    app = MusicDownloaderApp()
    app.run()
