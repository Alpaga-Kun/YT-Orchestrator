import argparse
from srcs import sound_providers

from rich.console import Console
from rich.status import Status
from time import sleep

class MusicDownloaderApp:
    def __init__(self):
        self.console = Console()

    def parse_arguments(self):
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

    def download_with_spinner(self, videos, provider, output_folder):
        """
        Affiche un spinner simple pendant le téléchargement de chaque vidéo.
        """
        for video in videos:
            title = video.get("title", "Unknown Title")
            url = video.get("url", video.get("webpage_url"))

            with Status(f"[bold cyan]Downloading: {title}[/]", spinner="dots", console=self.console):
                provider.download_video(url, output_folder)
                sleep(0.1)  # Pause pour une transition fluide

            self.console.print(f"[bold green]Completed:[/] {title}")

    def run(self):
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

            # Télécharger les vidéos avec un spinner
            self.download_with_spinner(videos, provider, args.output_folder)

            self.console.print(f"[bold green]Files have been downloaded to: {args.output_folder}[/]")
        else:
            self.console.print(f"[bold red]Provider '{provider_name}' not found. Please check available providers.[/]")

if __name__ == "__main__":
    app = MusicDownloaderApp()
    app.run()
