import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import numpy as np
# 1: Chargement des données
path = r'L:\BUT\SD\Promo 2024\talshawwa\SAE_web_Scrapping\Data_JV.csv'
df = pd.read_csv(path, sep=';', encoding='latin1')


# On supprime les lignes qui n'ont pas d'année pour éviter le plantage
df = df.dropna(subset=['Annee'])
df['Annee'] = df['Annee'].astype(int)

# Configuration esthétique globale
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = [12, 6]

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Chargement des données 
path = r'L:\BUT\SD\Promo 2024\talshawwa\SAE_web_Scrapping\Data_JV.csv'
df = pd.read_csv(path, sep=';', encoding='latin1')


# 3. Création des tranches de 5 ans
min_year = df['Annee'].min()
max_year = df['Annee'].max()
# On crée des paliers tous les 5 ans
bins = list(range(int(min_year), int(max_year) + 6, 5))
labels = [f"{i}-{i+4}" for i in bins[:-1]]

df['Tranche_Années'] = pd.cut(df['Annee'], bins=bins, right=False, labels=labels)

# 4. Comptage des jeux par tranche
evolution_grouped = df['Tranche_Années'].value_counts().sort_index()

# 5. Création du graphique combiné (Barres + Courbe)
plt.rcParams['figure.figsize'] = [12, 7]
sns.set_theme(style="whitegrid")

# Tracer les barres
ax = sns.barplot(x=evolution_grouped.index, y=evolution_grouped.values, color='skyblue', alpha=0.7)

# AJOUT DE LA COURBE 
#placer les points au centre des barres
plt.plot(range(len(evolution_grouped)), evolution_grouped.values, 
         color='#4a77b4', marker='o', linewidth=3, label='Tendance')

# Étiquettes et mise en forme
plt.title('Volume de sorties et Tendance par tranches de 5 ans', fontsize=14)
plt.xlabel('Période', fontsize=12)
plt.ylabel('Nombre total de jeux', fontsize=12)
plt.xticks(rotation=45)

# Ajout des nombres exacts au-dessus des barres
for i, v in enumerate(evolution_grouped.values):
    plt.text(i, v + 5, str(int(v)), ha='center', fontweight='bold', color='#2c3e50')

plt.tight_layout()
plt.savefig('evolution_5_ans_mixte.png')
print("Graphique combiné sauvegardé : evolution_5_ans_mixte.png")



# --- VIZ 2: Top Développeurs ---
print("Génération du graphique des développeurs...")
plt.figure(figsize=(12, 8))
df_clean_dev = df[~df['Developpeur'].isin(['N/A', 'Unknown', 'nan', 'TBA'])]
top_devs = df_clean_dev['Developpeur'].value_counts().head(10)

sns.barplot(x=top_devs.values, y=top_devs.index, palette='magma')
plt.title('Top 10 des Studios de Développement')
plt.xlabel('Nombre de jeux sortis')

for index, value in enumerate(top_devs.values):
    plt.text(value + 0.1, index, str(value), va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('top_developpeurs_final.png')

# --- VIZ 3: Top Genres ---
print("Génération du graphique des genres...")
df_genres = df[df['Genres'].notna()]
all_genres = df_genres['Genres'].str.split(', ').explode()
top_genres = all_genres.value_counts().head(8)

plt.figure(figsize=(10, 6))
sns.barplot(x=top_genres.index, y=top_genres.values, palette='Spectral')
plt.title('Répartition par Genres')
plt.xticks(rotation=45)

for index, value in enumerate(top_genres.values):
    plt.text(index, value + 2, str(value), ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('top_genres_final.png')



# --- VIZ 4: Heatmap de Saisonnalité ---
print("Génération de la heatmap...")

# Nettoyage de la colonne "mois"
df_season = df.copy()
df_season['Mois'] = df_season['Mois'].str.strip()

# Definir l'ordre des mois

months_order = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
                "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]

# compter les jeux par mois
heatmap_data = df_season.groupby(['Mois', 'Annee']).size().unstack(fill_value=0)

# 4. Reorder months and filter years (e.g., last 10 years for better visibility)
existing_months = [m for m in months_order if m in heatmap_data.index]
heatmap_data = heatmap_data.reindex(existing_months)
heatmap_data = heatmap_data.iloc[:, -10:] # les 10 dernieres années

# Création du graphique 

plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, annot=True, fmt="g", cmap="YlOrRd", linewidths=.5)

plt.title('Densité des sorties par mois et année', fontsize=14)
plt.ylabel('Mois')
plt.xlabel('Année')

plt.savefig('heatmap_finale_fr.png')

# --- VIZ 5: Corrélation Score vs Temps de Jeu ---

# Extraction des chiffres du temps de jeu 
df['Playtime_Num'] = df['Temps moyen de jeu'].str.extract('(\d+)').astype(float)
# On s'assure que le Metascore est numérique et on enlève les lignes vides
df_clean = df.dropna(subset=['Metascore', 'Playtime_Num'])
df_clean = df_clean[df_clean['Playtime_Num'] > 0] 


# On calcule la corrélation entre le score et le LOG du temps de jeu
corr, _ = pearsonr(np.log10(df_clean['Playtime_Num']), df_clean['Metascore'])

# Création du graphique 
plt.figure(figsize=(12, 7))
sns.set_theme(style="whitegrid")

# Nuage de points avec une légère transparence
sns.scatterplot(data=df_clean, x='Playtime_Num', y='Metascore', 
                alpha=0.5, color='#6a1b9a', label='Jeux individuels')

# AJOUT : Échelle logarithmique sur l'axe X
plt.xscale('log')

# AJOUT : Courbe LOESS (Tendance non-linéaire souple)
sns.regplot(data=df_clean, x='Playtime_Num', y='Metascore', 
            scatter=False, color='red')

# AJOUT : Affichage du coefficient de corrélation $r$ sur le graphique
plt.text(0.05, 0.95, f'Corrélation Pearson $r = {corr:.2f}$', 
         transform=plt.gca().transAxes, fontsize=12, 
         fontweight='bold', bbox=dict(facecolor='white', alpha=0.8))

# Étiquettes et finitions
plt.title('Analyse : Influence de la durée de vie sur la qualité (Échelle Log)', fontsize=14)
plt.xlabel('Temps de jeu moyen (Heures - Échelle Log)', fontsize=12)
plt.ylabel('Metascore / 100', fontsize=12)
plt.grid(True, which="both", ls="-", alpha=0.5)
plt.legend()

plt.tight_layout()
plt.savefig('correlation_top_level.png')
print(f"Graphique amélioré sauvegardé ! Corrélation calculée : {corr:.2f}")


# --- VIZ : QUALITÉ DES STUDIOS (BARRES VERTICALES & COULEURS INVERSÉES) ---
print("Génération du graphique de qualité (Vertical)...")

# Groupement par développeur et calcul de la moyenne
dev_stats = df.groupby('Developpeur').agg({'Metascore': ['mean', 'count']})
dev_stats.columns = ['Score_Moyen', 'Nombre_Jeux']

# Filtrer pour les studios avec au moins 3 jeux et trier
top_rated = dev_stats[dev_stats['Nombre_Jeux'] > 2].sort_values(by='Score_Moyen', ascending=False).head(10)

plt.figure(figsize=(14, 8))

# Changement : x=index (noms), y=values (scores) pour verticalité
# Changement : palette 'RdYlGn_r' pour passer du vert (haut) au rouge (bas)
sns.barplot(x=top_rated.index, y=top_rated['Score_Moyen'], hue=top_rated.index, 
            palette='RdYlGn_r', legend=False)

# Réglages des axes
plt.ylim(70, 100) # Zoom sur la zone de haute qualité
plt.title('Top 10 Studios par Qualité (Score Moyen - Min. 3 jeux)', fontsize=14)
plt.ylabel('Score Metascore Moyen', fontsize=12)
plt.xlabel('Studio de Développement', fontsize=12)
plt.xticks(rotation=45, ha='right') # Rotation des noms pour lisibilité

# Ajout des étiquettes de score au-dessus des barres
for i, v in enumerate(top_rated['Score_Moyen']):
    plt.text(i, v + 0.5, f"{v:.1f}", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig('final_top_qualite_vertical.png')
print("Graphique vertical de qualité sauvegardé !")


print("Fini !")


plt.show()