import os
import zipfile
from typing import List
from azure.storage.blob import BlobServiceClient


class Utils:
    def __init__(self, AZURE_STORAGE_CONNECTION_STRING: str, container_name: str):
        """
        Initialise l'outil avec les paramètres Azure Blob Storage.

        Args:
            AZURE_STORAGE_CONNECTION_STRING (str): Chaîne de connexion pour Azure Blob Storage.
            container_name (str): Nom du conteneur Azure Blob Storage.
        """
        self.AZURE_STORAGE_CONNECTION_STRING = AZURE_STORAGE_CONNECTION_STRING
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

    def compress_folder(self, folder_path: str, output_zip: str) -> str:
        """
        Compresse un dossier en fichier ZIP.

        Args:
            folder_path (str): Chemin du dossier à compresser.
            output_zip (str): Nom du fichier ZIP de sortie.

        Returns:
            str: Chemin du fichier ZIP compressé.
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)

        print(f"Folder {folder_path} compressed to {output_zip}")
        return output_zip

    def upload_to_blob_storage(self, file_path: str) -> str:
        """
        Uploade un fichier vers Azure Blob Storage.

        Args:
            file_path (str): Chemin du fichier local à uploader.

        Returns:
            str: URL du fichier uploadé dans Blob Storage.
        """
        container_client = self.blob_service_client.get_container_client(self.container_name)

        # Créer le conteneur s'il n'existe pas
        if not container_client.exists():
            container_client.create_container()
            print(f"Created container: {self.container_name}")

        blob_name = os.path.basename(file_path)
        blob_client = container_client.get_blob_client(blob_name)

        # Uploader le fichier
        with open(file_path, "rb") as file_data:
            blob_client.upload_blob(file_data, overwrite=True)
            print(f"Uploaded {file_path} to Azure Blob Storage as {blob_name}")

        # Générer un lien public
        return f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"

    def create_folder(self, folder_path: str) -> None:
        """
        Crée un dossier s'il n'existe pas.

        Args:
            folder_path (str): Chemin du dossier à créer.
        """
        os.makedirs(folder_path, exist_ok=True)
        print(f"Folder created or already exists: {folder_path}")

    def cleanup(self, file_paths: List[str]) -> None:
        """
        Supprime les fichiers locaux.

        Args:
            file_paths (List[str]): Liste des chemins des fichiers à supprimer.
        """
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted local file: {file_path}")
