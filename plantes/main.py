import os
import csv
import asyncio
from playwright.async_api import async_playwright
from tqdm import tqdm
import requests
from PIL import Image
from io import BytesIO

# Fichier CSV pour sauvegarder les métadonnées des images
SOURCES_FILE = "image_sources.csv"

def create_search_terms():
    """Demande à l'utilisateur les termes de recherche pour les plantes et maladies."""
    search_terms = {}
    print("\n=== Configuration des termes de recherche ===")
    while True:
        plant = input("\nEntrez le nom de la plante (ou 'q' pour quitter) : ").strip()
        if plant.lower() == "q":
            break
        diseases = input(f"Entrez les maladies pour {plant}, séparées par une virgule : ").split(",")
        search_terms[plant] = [disease.strip() for disease in diseases]
    return search_terms


async def fetch_image_urls(playwright, query, max_links_to_fetch):
    """Recherche les URLs des images et leurs sources."""
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    search_url = f"https://www.google.com/search?tbm=isch&q={query}"
    await page.goto(search_url)

    image_urls = set()
    metadata = []
    scroll_pause_time = 2

    print(f"\nRecherche des images pour : {query}")
    while len(image_urls) < max_links_to_fetch:
        thumbnails = await page.query_selector_all("img.Q4LuWd")
        for img in thumbnails[len(image_urls):]:
            try:
                await img.click()
                await page.wait_for_timeout(1000)
                images = await page.query_selector_all("img.n3VNCb")
                for image in images:
                    src = await image.get_attribute("src")
                    if src and "http" in src:
                        page_url = page.url
                        image_urls.add(src)
                        metadata.append((query, src, page_url))
                        if len(image_urls) >= max_links_to_fetch:
                            break
            except Exception as e:
                print(f"Erreur lors de la collecte : {e}")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(scroll_pause_time * 1000)

    await browser.close()
    return list(image_urls), metadata


def download_images(folder_path, metadata):
    """Télécharge et sauvegarde les images avec leurs sources."""
    os.makedirs(folder_path, exist_ok=True)
    with open(SOURCES_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for i, (query, url, source_page) in enumerate(
            tqdm(metadata, desc=f"Téléchargement vers {folder_path}")
        ):
            try:
                response = requests.get(url, timeout=5)
                img = Image.open(BytesIO(response.content))
                img = img.convert("RGB")
                img.save(os.path.join(folder_path, f"image_{i+1}.jpg"), "JPEG")
                writer.writerow([query, url, source_page])
            except Exception as e:
                print(f"Erreur téléchargement {url}: {e}")


async def main():
    """Fonction principale pour gérer la collecte et le téléchargement."""
    print("\n=== Bienvenue dans l'outil de téléchargement d'images de plantes ===")
    search_terms = create_search_terms()

    # Demander le nombre d'images par catégorie
    while True:
        try:
            num_images = int(input("\nEntrez le nombre d'images à télécharger par maladie : "))
            break
        except ValueError:
            print("Veuillez entrer un nombre valide.")

    # Initialisation du fichier CSV
    with open(SOURCES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Search Term", "Image URL", "Source Page"])

    # Recherche et téléchargement des images
    async with async_playwright() as playwright:
        for plant, diseases in search_terms.items():
            for disease in diseases:
                print(f"\nRecherche d'images pour {disease} ({plant})...")
                folder_name = f"Plant_Disease_Images/{plant}/{disease.replace(' ', '_')}"
                image_urls, metadata = await fetch_image_urls(playwright, f"{disease} plante", num_images)
                download_images(folder_name, metadata)

    print("\nTéléchargement terminé ! Toutes les images sont sauvegardées.")


if __name__ == "__main__":
    asyncio.run(main())
