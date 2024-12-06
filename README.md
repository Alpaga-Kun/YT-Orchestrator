# 🎵 **YT-Orchestrator** 🎵

Bienvenue dans **YT-Orchestrator**, une application Python conçue pour révolutionner votre manière de télécharger, organiser et sauvegarder vos musiques préférées. Ce projet permet de télécharger des musiques depuis diverses plateformes, de les organiser proprement, de compresser les fichiers et de les sauvegarder dans le cloud pour un accès facile et sécurisé. 🎧✨

---

## **🚀 Fonctionnalités**

### 🎵 **Téléchargement de Musiques**
- **Support Multi-Provider** : 
  - YouTube : Téléchargez des playlists ou vidéos individuelles en haute qualité.
  - Spotify : Analysez vos playlists pour télécharger les musiques associées via des plateformes tierces.
- **Téléchargement Multi-threadé** : Profitez d’une vitesse de téléchargement optimisée grâce à l'utilisation de threads.
- **Évitement des doublons** : Vérifiez si une musique a déjà été téléchargée pour éviter des fichiers en double.

### 🗂️ **Organisation Automatique**
- Téléchargement organisé dans des dossiers nommés d’après les titres des playlists.
- Support JSON pour gérer plusieurs playlists en une seule exécution.
- Gestion d’un dossier unique pour les téléchargements individuels.

### 🔒 **Sauvegarde Cloud**
- **Azure Blob Storage** (ou OneDrive) :
  - Compression automatique des musiques téléchargées en fichiers ZIP.
  - Téléchargement des fichiers compressés sur le cloud.
  - Génération d'un lien public pour accéder facilement aux fichiers.
- Nettoyage automatique des fichiers locaux après une sauvegarde réussie.

### 🛠️ **Fonctionnalités Utilitaires**
- **Compression efficace** : Compactez les fichiers audio sans perte de qualité.
- **Gestion des erreurs** : Listez toutes les erreurs de téléchargement pour un diagnostic facile.
- **Nettoyage intelligent** : Supprimez les fichiers compressés après leur upload pour économiser de l'espace disque.

### 💻 **Expérience Utilisateur Améliorée**
- Interface console optimisée avec des spinners et des indicateurs visuels grâce à `rich`.
- Affichage en temps réel des musiques téléchargées.
- Résumé clair des téléchargements réussis et des erreurs.

---

## **📂 Structure du Projet**

```
.
├── config
│   └── playlists.json       # Fichier JSON pour gérer les playlists
│   └── .env                 # Variables d'environnement (non inclus dans le repo)
├── srcs
│   ├── __init__.py
│   ├── base_soundprovider.py # Classe de base pour les providers
│   ├── providers
│   │   ├── youtube.py        # Téléchargement depuis YouTube
│   │   ├── spotify.py        # Analyse des playlists Spotify
│   └── utils.py              # Outils pour compression, sauvegarde et nettoyage
├── main.py                   # Point d'entrée principal
├── README.md                 # Documentation du projet
├── requirements.txt          # Dépendances du projet
```

---

## **📦 Installation**

### **1. Prérequis**
- **Python 3.9+**
- **Compte Azure** (ou OneDrive pour stockage alternatif)
- **pip** pour la gestion des dépendances

### **2. Installation**
1. Clonez le dépôt :
   ```bash
   git clone https://github.com/Alpaga-Kun/YT-Orchestrator.git
   cd YT-Orchestrator
   ```

2. Installez les dépendances nécessaires :
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez vos variables d'environnement dans un fichier `.env` :
   ```env
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=musicoff;AccountKey=your_key;EndpointSuffix=core.windows.net
   ```

4. Créez un fichier `playlists.json` dans le dossier `config` :
   ```json
   {
       "playlists": [
           {
               "title": "My Favorite Songs",
               "url": "https://youtube.com/playlist?list=..."
           },
           {
               "title": "Workout Tracks",
               "url": "https://youtube.com/playlist?list=..."
           }
       ]
   }
   ```

---

## **✨ Utilisation**

### **Télécharger une Playlist Unique**
Utilisez l’URL directe de la playlist :
```bash
python main.py --provider youtube --playlist-url "https://youtube.com/playlist?list=..." --output-folder downloads
```

### **Télécharger plusieurs Playlists depuis un JSON**
Faites référence à un fichier JSON contenant plusieurs playlists :
```bash
python main.py --provider youtube --playlists-json config/playlists.json --output-folder downloads
```

### **Sauvegarder automatiquement sur le Cloud**
- Les musiques téléchargées sont compressées en un fichier ZIP.
- Le fichier compressé est envoyé sur Azure Blob Storage, et un lien public est généré.

---

## **⚙️ Fonctionnement Interne**

### **Téléchargement**
1. **Provider** :
   - Sélectionnez la plateforme (YouTube, Spotify, etc.) à l’aide de `--provider`.
2. **Multi-threading** :
   - Téléchargement accéléré grâce à des threads gérés avec des mutex pour éviter les conflits.

### **Compression et Sauvegarde**
1. **Compression** :
   - Dossier compressé en ZIP.
   - Réduction de l'espace disque utilisé sans compromettre la qualité audio.
2. **Cloud** :
   - Fichiers compressés sauvegardés sur Azure Blob Storage avec un lien généré pour un partage rapide.

### **Nettoyage**
- Suppression automatique des fichiers ZIP locaux une fois sauvegardés.

---

## **📋 Roadmap**

1. **Ajout de nouveaux providers** :
   - SoundCloud, Deezer, etc.
2. **Support des métadonnées enrichies** :
   - Artistes, albums, pochettes.
3. **Optimisation des performances** :
   - Téléchargement parallèle amélioré pour de très grandes playlists.
4. **Notifications** :
   - Alertes par e-mail ou Discord après l’exécution du script.

---

## **👩‍💻 Contribution**

1. Clonez le dépôt et créez une nouvelle branche :
   ```bash
   git checkout -b ma-branche
   ```
2. Soumettez une **Pull Request** avec vos modifications.

---

## **📝 Licence**

Ce projet est sous licence MIT. Consultez le fichier `LICENSE` pour plus d'informations.

---

### 🎉 **Merci d'utiliser Music Downloader & Organizer !**
Si vous avez des suggestions ou des questions, n'hésitez pas à ouvrir une issue. Profitez de vos musiques téléchargées et organisées sans effort ! 🎶
