# Script de scraping pour le site rawg.io
# Collecte automatiquement les infos de jeux vidéo en utilisant selenium

print("Installation des packages en cours")
!pip install -q selenium pandas openpyxl beautifulsoup4 webdriver-manager

# Installation de chrome
print("Installation de Chrome en cours")
!apt-get update > /dev/null 2>&1
!apt-get install -y wget unzip > /dev/null 2>&1
!wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
!apt-get install -y ./google-chrome-stable_current_amd64.deb > /dev/null 2>&1
!rm google-chrome-stable_current_amd64.deb
print("Installation terminée!\n")

# Importation des bibliothèques
import pandas as pd  # pour créer et manipuler des tableaux de données
import time  # pour ajouter des pauses entre les requêtes
import re  # pour chercher des patterns dans du texte (dates, etc.)
from bs4 import BeautifulSoup  # pour extraire facilement des infos du html
from datetime import datetime  # pour gérer les dates et calculer le temps d'exécution
from selenium import webdriver  # pour contrôler le navigateur automatiquement
from selenium.webdriver.chrome.service import Service  # pour configurer chromedriver
from selenium.webdriver.chrome.options import Options  # pour configurer les options de chrome
from selenium.webdriver.common.by import By  # pour spécifier comment trouver les éléments html
from webdriver_manager.chrome import ChromeDriverManager  # pour télécharger automatiquement le bon chromedriver

# Configuration de chrome pour qu'il fonctionne sans interface graphique et soit plus discret
chrome_options = Options()

chrome_options.add_argument("--headless=new")  # chrome s'exécute sans fenêtre visible
chrome_options.add_argument("--no-sandbox")  # nécessaire pour google colab
chrome_options.add_argument("--disable-dev-shm-usage")  # évite les problèmes de mémoire
chrome_options.add_argument("--disable-gpu")  # pas besoin d'accélération gpu en headless
chrome_options.add_argument("--window-size=1920,1080")  # taille de la fenêtre virtuelle
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # masque l'automatisation pour pas être détecté comme bot
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")  # simule un vrai navigateur
chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # désactive les images pour aller plus vite

try:
    # Démarrage du navigateur chrome
    service = Service(ChromeDriverManager().install())  # télécharge chromedriver automatiquement
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    debut = datetime.now()  # on enregistre l'heure de début
    
    #====================================================
    # Etape 1 : on collecte tous les liens vers les jeux
    #====================================================
    print("Etape 1 : Collecte des URLs sur toutes les pages disponibles")
    
    urls_collectees = set()  # on utilise un set pour éviter les doublons
    page_num = 1
    pages_vides_consecutives = 0  # compteur pour savoir quand s'arrêter
    
    # On parcourt toutes les pages jusqu'à en trouver 3 vides d'affilée
    while True:
        try:
            url = f"https://rawg.io/games?page={page_num}"
            driver.get(url)  # on charge la page
            time.sleep(1.5)  # on attend que la page se charge
            
            # On fait défiler la page car certains sites chargent le contenu au scroll
            for _ in range(2):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
            
            # On récupère tous les liens vers les jeux
            elements = driver.find_elements(By.CLASS_NAME, 'game-card-medium__info__name')
            nouveaux = [el.get_attribute('href') for el in elements if el.get_attribute('href')]
            
            # Si la page est vide on compte, sinon on réinitialise le compteur
            if not nouveaux:
                pages_vides_consecutives += 1
                print(f"   Page {page_num} : Aucun jeu trouvé ({pages_vides_consecutives}/3)")
                if pages_vides_consecutives >= 3:
                    print(f"   Arrêt : 3 pages vides consécutives")
                    break
            else:
                pages_vides_consecutives = 0
                urls_collectees.update(nouveaux)  # on ajoute les nouveaux liens
                
                if page_num % 10 == 0:
                    print(f"   Page {page_num} : {len(urls_collectees)} URLs uniques collectées")
            
            page_num += 1
            
            # Limite de sécurité pour éviter une boucle infinie
            if page_num > 500:
                print(f"   Arrêt : Limite de 500 pages atteinte")
                break
        
        except Exception as e:
            print(f"   Erreur page {page_num}: {e}")
            pages_vides_consecutives += 1
            if pages_vides_consecutives >= 3:
                break
            page_num += 1
            continue
    
    urls_a_visiter = list(urls_collectees)
    print(f"\nTotal : {len(urls_a_visiter)} URLs uniques collectées")
    print(f"Extraction de tous les jeux 100% complets...\n")
    
     #=======================================================
    # Etape 2 : on visite chaque jeu et on extrait les infos
     #=======================================================
    print("Etape 2 : Extraction des jeux (critères ultra stricts)")
    print("=" * 60)
    
    jeux_parfaits = []  # On ne garde que les jeux avec toutes les infos
    jeux_rejetes = 0
    
    # On suit pourquoi les jeux sont rejetés
    stats_rejets = {
        "Titre manquant": 0,
        "Genres manquants": 0,
        "Date manquante": 0,
        "Développeur manquant": 0,
        "Éditeur manquant": 0,
        "Metascore manquant": 0,
        "Temps de jeu manquant": 0
    }
    
    # Fonction qui vérifie qu'un jeu a toutes les infos
    def est_parfait(jeu):
        if not jeu["Titre"] or jeu["Titre"] == "N/A" or jeu["Titre"] == "":
            stats_rejets["Titre manquant"] += 1
            return False
        if not jeu["Genres"] or jeu["Genres"] == "N/A" or jeu["Genres"] == "":
            stats_rejets["Genres manquants"] += 1
            return False
        if not jeu["Date_Raw"] or jeu["Date_Raw"] == "N/A" or jeu["Date_Raw"] == "":
            stats_rejets["Date manquante"] += 1
            return False
        if not jeu["Developpeur"] or jeu["Developpeur"] == "N/A" or jeu["Developpeur"] == "":
            stats_rejets["Développeur manquant"] += 1
            return False
        if not jeu["Editeur"] or jeu["Editeur"] == "N/A" or jeu["Editeur"] == "":
            stats_rejets["Éditeur manquant"] += 1
            return False
        if not jeu["Metascore"] or jeu["Metascore"] == "N/A" or jeu["Metascore"] == "":
            stats_rejets["Metascore manquant"] += 1
            return False
        if not jeu["Temps moyen de jeu"] or jeu["Temps moyen de jeu"] == "N/A" or jeu["Temps moyen de jeu"] == "":
            stats_rejets["Temps de jeu manquant"] += 1
            return False
        return True
    
    # On parcourt tous les jeux
    for i, link in enumerate(urls_a_visiter, 1):
        try:
            driver.get(link)
            time.sleep(0.8)
            
            # On parse le html avec beautifulsoup c'est plus simple que selenium
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extraction du titre
            h1 = soup.find('h1', class_='heading_1')
            titre = h1.get_text(strip=True) if h1 else "N/A"
            
            # Par défaut tout est à N/A
            developer = "N/A"
            publisher = "N/A"
            genres = "N/A"
            metascore = "N/A"
            date_brute = "N/A"
            playtime = "N/A"
            
            # Extraction des métadonnées dans les blocs game__meta-block
            meta_blocks = soup.find_all('div', class_='game__meta-block')
            
            for block in meta_blocks:
                title_div = block.find('div', class_='game__meta-title')
                if not title_div:
                    continue
                
                title_text = title_div.get_text(strip=True)
                text_div = block.find('div', class_='game__meta-text')
                
                if text_div:
                    raw_text = text_div.get_text(strip=True, separator=',')
                    valeur = ", ".join([x.strip() for x in raw_text.split(',') if x.strip()])
                    
                    # On associe la valeur au bon champ
                    if valeur:
                        if 'Developer' in title_text:
                            developer = valeur
                        elif 'Publisher' in title_text:
                            publisher = valeur
                        elif 'Genre' in title_text:
                            genres = valeur
                        elif 'Metascore' in title_text:
                            metascore = valeur
                        elif 'Release date' in title_text:
                            date_brute = valeur
            
            # Extraction du temps de jeu
            pt_div = soup.find('div', class_='game__meta-playtime')
            if pt_div:
                pt_text = pt_div.get_text(strip=True).replace('Average Playtime:', '').strip()
                if pt_text:
                    playtime = pt_text
            
            # Création de l'objet jeu
            jeu = {
                "Titre": titre,
                "Metascore": metascore,
                "Date_Raw": date_brute,
                "Genres": genres,
                "Temps moyen de jeu": playtime,
                "Developpeur": developer,
                "Editeur": publisher,
                "URL": link
            }
            
            # On ne garde que les jeux parfaits
            if est_parfait(jeu):
                jeux_parfaits.append(jeu)
                
                # Affichage de la progression tous les 25 jeux
                if len(jeux_parfaits) % 25 == 0:
                    temps_ecoule = (datetime.now() - debut).total_seconds()
                    vitesse = i / temps_ecoule if temps_ecoule > 0 else 0
                    temps_restant = (len(urls_a_visiter) - i) / vitesse if vitesse > 0 else 0
                    heures = int(temps_restant // 3600)
                    minutes = int((temps_restant % 3600) // 60)
                    taux_reussite = (len(jeux_parfaits) / i * 100) if i > 0 else 0
                    
                    print(f"   [{len(jeux_parfaits)} parfaits] [{i}/{len(urls_a_visiter)}] "
                          f"{titre[:35]}... (Taux: {taux_reussite:.1f}% | ETA: {heures}h{minutes:02d}m)")
                
                # Sauvegarde tous les 200 jeux au cas où colab se ferme
                if len(jeux_parfaits) % 200 == 0:
                    pd.DataFrame(jeux_parfaits).to_excel(f"backup_{len(jeux_parfaits)}_parfaits.xlsx", index=False)
                    print(f"   [Sauvegarde: {len(jeux_parfaits)} jeux parfaits | Rejetés: {jeux_rejetes}]")
            else:
                jeux_rejetes += 1
        
        except Exception:
            jeux_rejetes += 1
            continue
    
     #=================================================
    # Etape 3 : on traite les données et on sauvegarde
     #=================================================
    if jeux_parfaits:
        df = pd.DataFrame(jeux_parfaits)  # conversion en tableau pandas
        
        # Traitement des dates
        mois_map = {
            "Jan": "Janvier", "Feb": "Février", "Mar": "Mars", "Apr": "Avril",
            "May": "Mai", "Jun": "Juin", "Jul": "Juillet", "Aug": "Août",
            "Sep": "Septembre", "Oct": "Octobre", "Nov": "Novembre", "Dec": "Décembre"
        }
        
        def traiter_date(d):
            try:
                # Cherche un pattern type "jan 2023"
                match = re.search(r'([A-Z][a-z]{2}).*(\d{4})', str(d))
                if match:
                    return mois_map.get(match.group(1), match.group(1)), int(match.group(2))
                # Si pas de mois, cherche juste l'année
                match_year = re.search(r'(\d{4})', str(d))
                if match_year:
                    return "Inconnu", int(match_year.group(1))
            except:
                pass
            return "Inconnu", None
        
        df['Mois'], df['Annee'] = zip(*df['Date_Raw'].apply(traiter_date))
        df = df.drop(columns=['Date_Raw'])
        
        # Réorganisation des colonnes
        cols = ['Titre', 'Metascore', 'Mois', 'Annee', 'Genres', 'Temps moyen de jeu',
                'Developpeur', 'Editeur', 'URL']
        df = df[cols]
        
        # Sauvegarde du fichier excel
        nom_fichier = f"Jeux_RAWG_{len(df)}.xlsx"
        df.to_excel(nom_fichier, index=False)
        
        # Calcul des stats finales
        temps_total = datetime.now() - debut
        heures = int(temps_total.total_seconds() // 3600)
        minutes = int((temps_total.total_seconds() % 3600) // 60)
        taux_reussite = (len(df) / len(urls_a_visiter) * 100) if urls_a_visiter else 0
        
        # Affichage du rapport final
        print("\n" + "=" * 60)
        print("Extraction terminée")
        print(f"Jeux parfaits récupérés : {len(df)}")
        print(f"Jeux rejetés : {jeux_rejetes}")
        print(f"URLs traitées : {len(urls_a_visiter)}")
        print(f"Taux de réussite : {taux_reussite:.1f}%")
        print(f"Temps total : {heures}h {minutes}min")
        print("Raisons des rejets")
        for raison, nb in sorted(stats_rejets.items(), key=lambda x: x[1], reverse=True):
            if nb > 0:
                print(f"   - {raison}: {nb} ({nb/jeux_rejetes*100:.1f}%)")
        print(f"\nFichier : {nom_fichier}")
        print("=" * 60)
        
        # Téléchargement du fichier
        from google.colab import files
        files.download(nom_fichier)
        
        # Vérification finale qu'il n'y a pas de n/a
        print("Dernière vérification :")
        tous_parfait = True
        for col in df.columns:
            nb_na = (df[col] == "N/A").sum()
            nb_vide = (df[col] == "").sum()
            nb_null = df[col].isna().sum()
            total_problemes = nb_na + nb_vide + nb_null
            
            if total_problemes > 0:
                print(f"   Erreur {col}: {total_problemes} valeurs manquantes")
                tous_parfait = False
            else:
                print(f"   OK {col}: 100% complet")
        
        if tous_parfait:
            print(" Pas de N.A dans le fichier")
        else:
            print("Attention N.A détectés")
        
        print("Aperçu des 5 premiers jeux :")
        print(df.head())
    
    else:
        print("Aucun jeu parfait trouvé.")

# Gestion des erreurs
except Exception as e:
    print(f"Erreur : {e}")
    import traceback
    traceback.print_exc()
    
    # Sauvegarde d'urgence si le script plante
    if 'jeux_parfaits' in locals() and jeux_parfaits:
        pd.DataFrame(jeux_parfaits).to_excel("sauvegarde_urgence.xlsx", index=False)
        print(f"Sauvegarde d'urgence : {len(jeux_parfaits)} jeux")
        from google.colab import files
        files.download("sauvegarde_urgence.xlsx")

# Nettoyage final
finally:
    if 'driver' in locals():
        driver.quit()  # On ferme le navigateur
        print("Navigateur fermé")
