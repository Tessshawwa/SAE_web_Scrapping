# Collecte et Traitement de données RAWG.io

Ce projet est un outil de Web Scraping conçu pour extraire, nettoyer et centraliser des informations historiques sur les jeux vidéo depuis la plateforme de référence RAWG.io.

L'objectif est de constituer une base de données fiable couvrant la période 1980-2024 afin d'analyser l'évolution de l'industrie : volume de sorties, notes critiques, temps de jeu et stratégies des studios.

Les données passent par un filtrage strict (rejet des données incomplètes) et un processus de nettoyage avant d'être exportées dans un fichier Excel exploitable pour de l'analyse statistique.

# Fonctionnalités

Collecte automatisée : Navigation via Selenium pour gérer la pagination dynamique et extraction rapide des métadonnées avec BeautifulSoup.

Filtrage Mode Strict : Le script rejette automatiquement tout jeu possédant une variable manquante (NaN) pour éviter de fausser les calculs de moyennes.

Nettoyage Intelligent :
Transformation des dates brutes en format structuré (Mois et Année séparés).
Harmonisation des genres et suppression des caractères spéciaux.
Gestion des erreurs et sauvegardes régulières pour éviter la perte de données en cours de route.

Export : Génération d'un dataset final propre au format .xlsx.

# Installation

1. Prérequis
Assurez-vous d'avoir Python 3.8 ou supérieur et le navigateur Google Chrome installés. Le script gère automatiquement le téléchargement du driver.

2. Cloner le projet
git clone https://github.com/votre-compte/votre-projet.git

3. Installer les bibliothèques
Le projet utilise les bibliothèques suivantes pour le pilotage du navigateur et la manipulation des données :

pip install selenium pandas openpyxl beautifulsoup4 webdriver-manager

# Structure des fichiers

scraping_rawg.py : Script principal orchestrant la collecte, le filtrage et le nettoyage.
Jeux_RAWG.xlsx : Fichier de sortie contenant le dataset final nettoyé.
Rapport scraping.pdf : Rapport d'analyse complet détaillant les tendances observées.
backup_parfaits.xlsx : Fichiers de sauvegarde générés automatiquement durant l'exécution pour la sécurité.

# Utilisation

Lancez le script de collecte :

python scraping_rawg.py

Le script va :
Parcourir les pages du site RAWG.io.
Extraire les informations techniques (Titre, Metascore, Editeur, Développeur, etc.).
Filtrer les jeux incomplets en temps réel.
Afficher une estimation du temps restant.

Une fois terminé, le fichier Excel final sera généré à la racine du dossier.

# Données traitées

Le dataset final inclut les colonnes suivantes :

Titre : Nom du jeu vidéo.
Metascore : Note de presse agrégée (sur 100).
Mois et Annee : Date de sortie traitée pour l'analyse temporelle.
Genres : Catégories du jeu (ex: Action, Aventure).
Temps moyen de jeu : Durée estimée par la communauté.
Developpeur : Studio de développement principal.
Editeur : L'entité responsable de la publication.

# Résultats de l'analyse

L'exploitation des données a permis de mettre en évidence plusieurs tendances détaillées dans le rapport PDF :

Explosion du Volume : Une croissance marquée des sorties, passant de moins de 200 jeux (2000-2004) à plus de 1000 jeux sur la période 2015-2019.

Qualité vs Durée : Une légère corrélation positive (r=0.28) indique que les jeux durant plus de 20h tendent à avoir de meilleures notes critiques, bien que la variabilité soit forte pour les jeux courts.

Saisonnalité : Une concentration systématique des sorties en septembre et octobre, reflétant une stratégie commerciale pour les fêtes de fin d'année.

Genres Dominants : Le genre Action domine largement la production (1868 titres), suivi de l'Aventure et de l'Indie.

# Répartition du travail

Nous avons réparti les tâches de la manière suivante :

Tasnim Alshawwa :
Extraction (10%) : Participation à la définition des variables.
Traitement (20%) : Support sur la gestion des données.
Visualisation (90%) : Création des graphiques, analyse des tendances et rédaction du rapport final.

Violette Grosjean :
Extraction (90%) : Développement du script de scraping, gestion des erreurs et filtrage des jeux.
Traitement (80%) : Transformation des données brutes en tableau structuré et nettoyage des colonnes.
Visualisation (10%) : Commentaires et interprétations complémentaires sur les graphiques.
