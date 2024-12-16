import os
import requests

def afficher_menu():
    print("\n=== Téléchargeur de documents ===")
    print("1. Télécharger un document")
    print("2. Définir le répertoire de destination")
    print("3. Quitter")

def telecharger_document(url, dossier_destination):
    try:
        # Extraire le nom du fichier depuis l'URL
        nom_fichier = url.split("/")[-1]
        chemin_complet = os.path.join(dossier_destination, nom_fichier)

        # Télécharger le fichier
        print(f"Téléchargement de {nom_fichier}...")
        reponse = requests.get(url, stream=True)
        reponse.raise_for_status()

        # Écrire le fichier sur le disque
        with open(chemin_complet, "wb") as fichier:
            for chunk in reponse.iter_content(chunk_size=8192):
                fichier.write(chunk)
        
        print(f"Document téléchargé avec succès : {chemin_complet}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement : {e}")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

def demander_repertoire():
    while True:
        dossier = input("\nEntrez le chemin du répertoire de destination : ").strip()
        if os.path.isdir(dossier):
            print(f"Répertoire défini : {dossier}")
            return dossier
        else:
            print("Le chemin spécifié n'existe pas. Essayez à nouveau.")

def main():
    dossier_destination = os.getcwd()  # Par défaut, le dossier courant
    while True:
        afficher_menu()
        choix = input("\nVotre choix : ").strip()
        if choix == "1":
            url = input("\nEntrez l'URL du document à télécharger : ").strip()
            if url:
                telecharger_document(url, dossier_destination)
            else:
                print("URL invalide. Essayez à nouveau.")
        elif choix == "2":
            dossier_destination = demander_repertoire()
        elif choix == "3":
            print("Au revoir !")
            break
        else:
            print("Choix invalide. Veuillez sélectionner une option valide.")

if __name__ == "__main__":
    main()
