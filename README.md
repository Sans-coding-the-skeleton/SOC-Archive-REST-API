# SOČ Archive REST API

REST API pro archiv prací SOČ (Středoškolská odborná činnost) podle specifikace softwarových požadavků.

## Funkce API

### Hlavní funkce
- Fulltextové vyhledávání prací
- Filtrování podle oboru, roku, školy, kraje, kategorie
- Zobrazení detailů práce s metadaty
- GDPR kompatibilita (odstranění osobních údajů)
- Import prací z externího systému
- Správa PDF souborů
- Administrátorské rozhraní

### API Endpoints

#### Práce (Works)
- `GET /api/works` - Seznam prací s filtrováním a vyhledáváním
- `GET /api/works/{id}` - Detail konkrétní práce
- `POST /api/works` - Vytvoření nové práce (import)
- `GET /api/works/{id}/pdf` - Stažení PDF souboru
- `DELETE /api/works/{id}/gdpr` - Odstranění osobních údajů (GDPR)

#### Kategorie
- `GET /api/categories` - Seznam kategorií
- `POST /api/categories` - Vytvoření nové kategorie

#### Administrace
- `POST /api/admin/works/{id}/approve` - Schválení práce
- `POST /api/admin/works/{id}/pdf` - Nahrání PDF souboru
- `GET /api/admin/stats` - Statistiky
- `GET /api/admin/export` - Export dat

## Požadavky na software

- Python 3.8+
- pip (správce balíčků Pythonu)

## Instalace a spuštění

1. **Naklonujte nebo stáhněte zdrojové kódy**

2. **Vytvořte virtuální prostředí (doporučeno)**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# nebo
venv\Scripts\activate  # Windows
```
3. **Nainstalujte závislosti**
```bash
pip install -r requirements.txt
```
4. **Spusťte aplikaci**
```bash
python app.py
```
5. **Otevřete prohlížeč a přejděte na:**
- API dokumentace: http://localhost:5000/api/
- Health check: http://localhost:5000/api/health