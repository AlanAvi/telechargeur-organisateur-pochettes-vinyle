from dotenv import load_dotenv
import os
import requests
from requests_oauthlib import OAuth1Session
import time

def getCollection():

    load_dotenv()
    CONSUMER_KEY = os.getenv("DISCOGS_CONSUMER_KEY")
    CONSUMER_SECRET = os.getenv("DISCOGS_CONSUMER_SECRET")
    REQUEST_TOKEN_URL = 'https://api.discogs.com/oauth/request_token'
    AUTHORIZE_URL = 'https://www.discogs.com/oauth/authorize'
    ACCESS_TOKEN_URL = 'https://api.discogs.com/oauth/access_token'

    # Session OAuth1
    oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET)

    # Token de demande
    fetch_response = oauth.fetch_request_token(REQUEST_TOKEN_URL)
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')

    print("Jeton de demande : ", resource_owner_key)
    print("Secret du jeton de demande : ", resource_owner_secret)

    authorization_url = oauth.authorization_url(AUTHORIZE_URL)
    print("Ouvre cette URL pour autoriser l'application : ", authorization_url)

    verifier = input("Entrez le code de vérification : ")

    # Token d'accès
    oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET,
                        resource_owner_key=resource_owner_key,
                        resource_owner_secret=resource_owner_secret,
                        verifier=verifier)

    access_token_response = oauth.fetch_access_token(ACCESS_TOKEN_URL)
    access_token = access_token_response.get('oauth_token')
    access_token_secret = access_token_response.get('oauth_token_secret')

    print("Jeton d'accès : ", access_token)
    print("Secret du jeton d'accès : ", access_token_secret)

    # Session OAuth1 avec le token d'accès
    oauth = OAuth1Session(CONSUMER_KEY, client_secret=CONSUMER_SECRET,
                        resource_owner_key=access_token,
                        resource_owner_secret=access_token_secret)

    # Endpoint pour la collection
    username = os.getenv("DISCOGS_USERNAME")
    url = f'https://api.discogs.com/users/{username}/collection/folders/0/releases?per_page=250'
    collection = []

    # Fonction pour récupérer toutes les pages de la collection
    def fetch_all_collection_data(url):
        while url:
            response = oauth.get(url)
            if response.status_code == 200:
                data = response.json()
                collection.extend(data.get('releases', []))  # Ajouter les éléments à la liste
                pagination = data.get('pagination', {})
                url = pagination.get('next', None)  # URL de la page suivante
            else:
                print(f"Erreur lors de la récupération des données de la collection : {response.status_code}")
                print(response.text)  # Afficher le texte de la réponse pour plus de détails
                break

    fetch_all_collection_data(url)

    print(f"Nombre total d'éléments dans la collection : {len(collection)}")

    # Créer le dossier 'covers' s'il n'existe pas
    if not os.path.exists('covers'):
        os.makedirs('covers')

    # En-têtes HTTP pour simuler une requête de navigateur
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    # Télécharger toutes les couvertures d'album
    missing_images = []
    for item in collection:
        basic_info = item.get('basic_information', {})
        cover_url = basic_info.get('cover_image')
        if cover_url:
            release_id = basic_info.get('id')
            cover_filename = f'covers/{release_id}.jpg'
            
            print(f"Téléchargement de la couverture pour l'album ID {release_id} depuis {cover_url}...")
            
            try:
                cover_response = requests.get(cover_url, headers=headers, stream=True)
                if cover_response.status_code == 200:
                    with open(cover_filename, 'wb') as file:
                        for chunk in cover_response.iter_content(chunk_size=1024):
                            if chunk:
                                file.write(chunk)
                    print(f"Couverture enregistrée : {cover_filename}")
                else:
                    print(f"Erreur lors du téléchargement de l'image pour l'album ID {release_id} : {cover_response.status_code}")
                    missing_images.append(release_id)  # Ajouter l'ID manquant à la liste
            except Exception as e:
                print(f"Exception lors du téléchargement de l'image pour l'album ID {release_id} : {e}")
                missing_images.append(release_id)  # Ajouter l'ID manquant à la liste
            time.sleep(2)
        else:
            print(f"Aucune URL de couverture trouvée pour l'album ID {basic_info.get('id')}")
            missing_images.append(basic_info.get('id'))  # Ajouter l'ID manquant à la liste

    print("Téléchargement des couvertures terminé.")
    
    # Afficher les IDs des images manquantes
    if missing_images:
        print("\nIDs des albums pour lesquels les couvertures sont manquantes :")
        print(missing_images)
    else:
        print("\nToutes les couvertures ont été téléchargées avec succès.")

    return collection

getCollection()