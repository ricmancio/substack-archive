# Substack to PDF Downloader

Script Python per scaricare automaticamente tutti gli articoli premium da qualsiasi newsletter Substack come PDF.

## 🚀 Installazione

### 1. Installa Python 3.8+
Assicurati di avere Python installato sul tuo sistema.

### 2. Installa le dipendenze
```bash
pip install -r requirements.txt
```

### 3. Installa Chrome/Chromium
Lo script richiede Google Chrome o Chromium installato.

### 4. Configura il file .env
Copia il file di esempio e configuralo con l'URL del tuo Substack:

```bash
cp .env.example .env
```

Modifica il file `.env` con l'URL della newsletter che vuoi scaricare:

```
SUBSTACK_BASE_URL=https://nome-newsletter.substack.com
```

Esempi di URL validi:
- `https://example.substack.com`
- `https://newsletter.example.com` (per domini personalizzati)

## 📖 Utilizzo

### Prima esecuzione
```bash
python substack_to_pdf.py
```

**Al primo avvio:**
1. Si aprirà automaticamente una finestra del browser
2. Effettua il login con le tue credenziali Substack
3. Torna al terminale e premi INVIO
4. I cookie verranno salvati automaticamente

### Esecuzioni successive
```bash
python substack_to_pdf.py
```

Lo script userà i cookie salvati, **non dovrai più fare il login**!

## 📁 Output

Tutti i PDF vengono salvati nella cartella `pdfs/` con il nome dell'articolo.

## ⚙️ Come funziona

1. **Autenticazione**: Al primo avvio, lo script apre il browser per il login manuale. I cookie vengono salvati in `substack_cookies.json`
2. **Estrazione link**: Naviga nell'archivio e raccoglie tutti i link degli articoli
3. **Download PDF**: Per ogni articolo, genera un PDF con formattazione completa
4. **Skip intelligente**: Salta gli articoli già scaricati

## 🔧 Personalizzazione

### Cambiare newsletter
Modifica `SUBSTACK_BASE_URL` nel file `.env`:

```
SUBSTACK_BASE_URL=https://altra-newsletter.substack.com
```

### Scaricare un range specifico di articoli
Modifica `START_FROM` e `STOP_AT` nello script `substack_to_pdf.py`:

```python
START_FROM = 1      # Da quale articolo iniziare (default: 1)
STOP_AT = None      # Dove fermarsi (default: None = scarica tutto)
```

Esempi:
- `START_FROM = 100` - Riprende dal 100° articolo
- `STOP_AT = 50` - Si ferma dopo il 50° articolo
- `START_FROM = 10, STOP_AT = 20` - Scarica solo gli articoli dal 10° al 20°

### Directory di output
I PDF vengono salvati in `pdfs/`. Per cambiarla, modifica il parametro `output_dir` nella funzione `save_as_pdf`.

## ⚠️ Note

- Lo script rispetta un delay di 2 secondi tra download per non sovraccaricare il server
- I PDF mantengono la formattazione originale degli articoli
- I cookie sono validi finché non fai logout da Substack

## 🐛 Troubleshooting

**"Nessun articolo trovato"**
- Cancella il file `substack_cookies.json` e rieffettua il login

**"chromedriver non trovato"**
- Lo script lo scaricherà automaticamente alla prima esecuzione

**Articoli mancanti**
- Verifica che il tuo abbonamento premium sia attivo

## 🔐 Privacy

I cookie sono salvati localmente in `substack_cookies.json` - **non condividerli** con nessuno!
