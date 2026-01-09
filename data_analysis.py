import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1: chargement des données
df = pd.read_csv('jData_JV.csv', sep=';')

# 2: Standardisation des noms de plateformes
# ce dictionnaire mappe les variations courantes aux noms standardisés
platform_map = {
    'Win': 'PC', 'WIN': 'PC', 'Windows': 'PC',
    'NS': 'Switch', 'NX': 'Switch', 'Nintendo Switch': 'Switch',
    'PS4': 'PS4', 'PlayStation 4': 'PS4',
    'PS5': 'PS5', 'PlayStation 5': 'PS5',
    'XBO': 'Xbox One',
    'XSX/S': 'Xbox Series', 'XBX/S': 'Xbox Series', 'XBS': 'Xbox Series',
    'DROID': 'Android', 'iOS': 'iOS'
}

def clean_platform_string(text):
    if pd.isna(text): return "Unknown"
    # fractionne par virgule, nettoie les espaces, mappe et recompose en utlisant le dictionnaire
    parts = [p.strip() for p in str(text).split(',')]
    standardized = [platform_map.get(p, p) for p in parts]
    # utilisation de set() pour éviter les doublons
    return ", ".join(sorted(list(set(standardized))))

df['Platform'] = df['Platform'].apply(clean_platform_string)

# Convertir 'Year' en entier pour une manipulation plus facile
df['Year'] = df['Year'].astype(int)

# Configuration esthétique globale
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = [12, 6]



# --- VIZ 1: Top Platforms ---

plt.figure()

# preparation des données pour le graphique
top_platforms = df['Platform'].str.split(', ').explode().value_counts().head(10)

# 2 : Création du graphique
top_platforms.plot(kind='bar', color='skyblue')

# 3: ETIQUETTES 
plt.title('Top 10 des plateformes les plus représentées')
plt.xlabel('Plateformes')            # Label for X axis
plt.ylabel('Nombre de jeux vidéo')   # Label for Y axis (The 0 to 2000 scale)

# 4: Ajout des nombres au-dessus des barres
plt.xticks(rotation=45)
plt.tight_layout()

# 5: Sauvegarde et affichage
plt.savefig('top_plateformes_labeled.png')
print("Graph 2 updated with Y-axis label!")
plt.show()
# --- VIZ 2: evolution ---
# 1: Création du graphique
plt.figure(figsize=(10, 6))
evolution = df['Year'].value_counts().sort_index()
plt.plot(evolution.index, evolution.values, marker='o', linestyle='-', color='#4a77b4', linewidth=3)

# 2: enlever les .0 des années
plt.xticks(evolution.index) 

# 3: Ajout des nombres au-dessus des points
for year, count in zip(evolution.index, evolution.values):
    # Ajout du texte légèrement au-dessus du point
    plt.text(year, count + 15, str(count), 
             ha='center', va='bottom', fontsize=12, fontweight='bold', color='#4a77b4')

# 4. Etiquettes
plt.title('Évolution du nombre de sorties de jeux (2020-2024)')
plt.xlabel('Année')
plt.ylabel('Nombre total de jeux')
plt.grid(True, linestyle='--', alpha=0.6)

# 5. Ajustement de l'axe Y pour éviter que les étiquettes ne soient coupées
plt.ylim(top=evolution.max() + 100)

plt.savefig('tendance_annuelle_finale.png')
print("Graphique sauvegardé : tendance_annuelle_finale.png")

# --- VIZ 3: Top Developers (2023-2024) ---
plt.figure(figsize=(12, 8))

# 1: Filtrer les années récentes
df_recent = df[df['Year'].isin([2023, 2024])].copy()

# 2: Filtrage des développeurs vides ou non informatifs
# On enlève les entrées où le développeur est 'N/A', 'Unknown', 'nan' ou 'TBA'
df_clean_dev = df_recent[~df_recent['Developer'].isin(['N/A', 'Unknown', 'nan', 'TBA'])]

# 3: Compter les occurrences des développeurs
top_devs = df_clean_dev['Developer'].value_counts().head(10)

# 4: Création du graphique
sns.barplot(x=top_devs.values, y=top_devs.index, palette='magma')

# 5: Etiquettes
plt.title('Top 10 des Studios de Développement (2023-2024)', fontsize=14)
plt.xlabel('Nombre de jeux sortis', fontsize=12)
plt.ylabel('Studio', fontsize=12)

# 6: Ajout des nombres à côté des barres
for index, value in enumerate(top_devs.values):
    plt.text(value + 0.5, index, str(value), va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('top_developpeurs_2023_2024.png')
print("Graphique sauvegardé : top_developpeurs_2023_2024.png")


# --- VIZ 3: Heatmap Saisonnalité (2020 - 2021) ---

# 1: Filtrer les années 2020 et 2021 (car il y a un problème avec 2022-2024)
df_seasonality = df[df['Year'].isin([2020, 2021])].copy()

# 2: Nettoyer les noms des mois
df_seasonality['Month'] = df_seasonality['Month'].str.strip()
months_order = ["January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"]

# 3: Préparer les données pour la heatmap
heatmap_data = df_seasonality.groupby(['Month', 'Year']).size().unstack(fill_value=0)
heatmap_data = heatmap_data.reindex(months_order)

# 4: Création de la heatmap
plt.figure(figsize=(8, 8))
sns.heatmap(heatmap_data, annot=True, fmt="g", cmap="YlOrRd", linewidths=.5)

# 5: Etiquettes
plt.title('Saisonnalité des sorties (Années de référence 2020-2021)', fontsize=14)
plt.ylabel('Mois', fontsize=12)
plt.xlabel('Année', fontsize=12)

plt.tight_layout()
plt.savefig('heatmap_saisonnalite_2020_2021.png')
print("Graphique sauvegardé : heatmap_saisonnalite_2020_2021.png")

# --- VIZ 4: Top genres ---

# 1: Préparation des données
df_genres = df[df['Genre'].notna()]
all_genres = df_genres['Genre'].str.split(', ').explode()

# Répartition par Macro-Genres
# 2: Définir un dictionnaire de mapping pour regrouper les genres similaires
genre_map = {
    # 1: RPG Family
    'Role-playing': 'RPG', 'Role-playing game': 'RPG',
    'Action role-playing': 'RPG', 'Action RPG': 'RPG',
    'Strategy role-playing': 'RPG', 'Tactical RPG': 'RPG', 'JRPG': 'RPG',
    
    # 2: THE ADVENTURE FAMILY (Story driven)
    'Adventure game': 'Adventure', 'Adventure': 'Adventure',
    'Action-adventure': 'Adventure', 
    'Visual novel': 'Adventure',       
    'Survival horror': 'Adventure',    
    'Point-and-click': 'Adventure',
    
    # 3: THE ACTION FAMILY (Reflex driven)
    'Action game': 'Action', 'Action': 'Action',
    'First-person shooter': 'Action', 'FPS': 'Action',
    'Third-person shooter': 'Action', 'Shooter': 'Action',
    'Shoot \'em up': 'Action',
    'Fighting game': 'Action', 'Fighting': 'Action',
    'Platform': 'Action', 'Platformer': 'Action',
    'Beat \'em up': 'Action', 'Hack and slash': 'Action',
    
    # 4: Autres genres
    'Simulation game': 'Simulation', 'Sim': 'Simulation',
    'Strategy game': 'Strategy',
    'Sports game': 'Sports', 'Racing game': 'Sports' # Grouping Racing with Sports
}

# 3: Appliquer le mapping
# si un genre n'est pas dans le dictionnaire, il reste inchangé
all_genres = all_genres.replace(genre_map)

# 4: les 8 genres 
top_genres = all_genres.value_counts().head(8)

# 5: Création du graphique
plt.figure(figsize=(10, 6))
sns.barplot(x=top_genres.index, y=top_genres.values, palette='Spectral')

plt.title('Répartition par "Macro-Genres" (2020-2024)', fontsize=14)
plt.ylabel('Nombre de jeux', fontsize=12)
plt.xlabel('Genre Principal', fontsize=12)
plt.xticks(rotation=0) # Pas de rotation quand les labels sont courts

# 6: Ajout des nombres au-dessus des barres
for index, value in enumerate(top_genres.values):
    plt.text(index, value + 10, str(value), ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('top_genres_grouped.png')
print("Graphique sauvegardé : top_genres_grouped.png")
plt.show()