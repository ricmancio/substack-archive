#!/usr/bin/env python3
"""
Script per scaricare articoli Substack come PDF mantenendo l'autenticazione premium
"""

import os
import time
import json
from urllib.parse import urlparse
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup

def setup_driver(cookies_file=None, base_url=None):
    """Configura il browser Chrome con opzioni per PDF"""
    chrome_options = Options()

    # Impostazioni per il download PDF
    settings = {
        "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": ""
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }

    prefs = {
        'printing.print_preview_sticky_settings.appState': json.dumps(settings),
        'savefile.default_directory': os.path.join(os.getcwd(), 'pdfs')
    }

    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument('--kiosk-printing')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    # Inizializza il driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    # Carica i cookie se esistono
    if cookies_file and os.path.exists(cookies_file) and base_url:
        driver.get(base_url)
        time.sleep(2)
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Impossibile aggiungere cookie: {e}")

    return driver

def save_cookies(driver, cookies_file):
    """Salva i cookie della sessione"""
    cookies = driver.get_cookies()
    with open(cookies_file, 'w') as f:
        json.dump(cookies, f)
    print(f"Cookie salvati in {cookies_file}")

def login_manually(driver, cookies_file, login_url):
    """Guida l'utente al login manuale"""
    print("\n" + "="*60)
    print("PRIMO ACCESSO - LOGIN RICHIESTO")
    print("="*60)
    print("\n1. Si aprirà una finestra del browser")
    print("2. Effettua il login con le tue credenziali Substack")
    print("3. Una volta loggato, torna qui e premi INVIO")
    print("\nI cookie verranno salvati per le prossime esecuzioni.")
    print("="*60 + "\n")

    driver.get(login_url)
    input("Premi INVIO dopo aver effettuato il login...")

    # Salva i cookie
    save_cookies(driver, cookies_file)
    print("✓ Cookie salvati con successo!\n")

def get_archive_links(driver, archive_url, domain):
    """Estrae tutti i link degli articoli dall'archivio"""
    print(f"Caricamento archivio: {archive_url}")
    driver.get(archive_url)
    time.sleep(3)

    # Scroll per caricare tutti gli articoli
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Estrai i link
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    links = []

    # Cerca link agli articoli
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/p/' in href and domain in href:
            if href not in links:
                links.append(href)

    print(f"Trovati {len(links)} articoli\n")
    return links

def save_as_pdf(driver, url, output_dir='pdfs'):
    """Salva la pagina come PDF"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Estrai titolo dall'URL
    title = url.split('/p/')[-1].split('?')[0]
    pdf_path = os.path.join(output_dir, f"{title}.pdf")
    
    # Salta se già esiste
    if os.path.exists(pdf_path):
        print(f"⊘ Già esistente: {title}")
        return True
    
    try:
        print(f"⟳ Scaricamento: {title}")
        driver.get(url)
        time.sleep(3)
        
        # Attendi che il contenuto sia caricato
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        
        # Stampa come PDF
        result = driver.execute_cdp_cmd("Page.printToPDF", {
            "printBackground": True,
            "landscape": False,
            "paperWidth": 8.27,  # A4
            "paperHeight": 11.69,
            "marginTop": 0.4,
            "marginBottom": 0.4,
            "marginLeft": 0.4,
            "marginRight": 0.4,
        })
        
        # Salva il PDF
        with open(pdf_path, 'wb') as f:
            import base64
            f.write(base64.b64decode(result['data']))
        
        print(f"✓ Salvato: {pdf_path}")
        return True
        
    except Exception as e:
        print(f"✗ Errore con {title}: {e}")
        return False

def main():
    """Funzione principale"""
    # Carica variabili d'ambiente
    load_dotenv()

    SUBSTACK_BASE_URL = os.getenv('SUBSTACK_BASE_URL')
    if not SUBSTACK_BASE_URL:
        print("Errore: SUBSTACK_BASE_URL non configurato nel file .env")
        return

    # Rimuovi slash finale se presente
    SUBSTACK_BASE_URL = SUBSTACK_BASE_URL.rstrip('/')
    SUBSTACK_DOMAIN = urlparse(SUBSTACK_BASE_URL).netloc

    COOKIES_FILE = 'substack_cookies.json'
    ARCHIVE_URL = f'{SUBSTACK_BASE_URL}/archive'
    LOGIN_URL = f'{SUBSTACK_BASE_URL}/account/login'

    # Imposta da quale articolo iniziare (1 = primo articolo, 520 = riprendi dal 520esimo)
    START_FROM = 1
    # Imposta dove fermarsi (None = scarica tutto, 50 = si ferma al 50esimo)
    STOP_AT = None
    
    print("\n" + "="*60)
    print("SUBSTACK TO PDF DOWNLOADER")
    print("="*60 + "\n")
    
    # Setup driver
    driver = setup_driver(COOKIES_FILE, SUBSTACK_BASE_URL)

    try:
        # Login se necessario
        if not os.path.exists(COOKIES_FILE):
            login_manually(driver, COOKIES_FILE, LOGIN_URL)
        else:
            print("✓ Cookie trovati, uso la sessione salvata\n")

        # Ottieni lista articoli
        links = get_archive_links(driver, ARCHIVE_URL, SUBSTACK_DOMAIN)
        
        if not links:
            print("Nessun articolo trovato. Controlla l'autenticazione.")
            return
        
        # Scarica ogni articolo
        end_at = STOP_AT if STOP_AT else len(links)
        if START_FROM > 1 or STOP_AT:
            print(f"\nDownload articoli da {START_FROM} a {end_at} (totale: {len(links)})...\n")
        else:
            print(f"\nInizio download di {len(links)} articoli...\n")

        success_count = 0

        for i, link in enumerate(links, 1):
            # Salta gli articoli prima di START_FROM
            if i < START_FROM:
                continue
            # Ferma se supera STOP_AT
            if STOP_AT and i > STOP_AT:
                break

            print(f"[{i}/{len(links)}] ", end="")
            if save_as_pdf(driver, link):
                success_count += 1
            time.sleep(2)  # Pausa tra download
        
        print("\n" + "="*60)
        print(f"COMPLETATO: {success_count}/{len(links)} articoli scaricati")
        print(f"PDF salvati in: {os.path.join(os.getcwd(), 'pdfs')}")
        print("="*60 + "\n")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
