<div align="center">

# 🌍 Bosque County Parcel Scraper

### Central Texas Integrated Energy & Compute Zone

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-success)](https://williambevans.github.io/bosqueTriangle/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen)]()

**Professional-grade** Python scraper and interactive web visualization for Bosque County, Texas parcel data. Track solar development, active leases, and open land across **130,000 acres** of strategic energy corridor.

[View Live Demo](https://williambevans.github.io/bosqueTriangle/) • [Documentation](#-documentation) • [Quick Start](#-quick-start)

---

</div>

## ✨ Features

<table>
<tr>
<td>

**🗺️ Interactive Map**
- Dark-themed professional interface
- Real-time parcel visualization
- Development phase overlays
- POI markers & transmission lines

</td>
<td>

**⚡ Solar Tracking**
- Solar developed parcels
- Active lease identification
- Open land analysis
- Progress visualization

</td>
</tr>
<tr>
<td>

**📊 Data Export**
- JSON (nested structure)
- GeoJSON (QGIS compatible)
- CSV (spreadsheet analysis)
- GitHub Pages deployment

</td>
<td>

**🔧 Developer Tools**
- ArcGIS REST API scraper
- Automated endpoint discovery
- Field mapping system
- Rate limiting & retries

</td>
</tr>
</table>

---

## 🎯 Target Area

```
┌─────────────────────────────────────────────┐
│  Clifton (SW):     -97.5769, 31.7823       │
│  Lake Whitney (N): -97.3618, 31.9508       │
│  McLennan/Hwy 6:   -97.2891, 31.7234       │
│                                             │
│  Coverage: ~130,000 acres                  │
│  County: Bosque, Texas                     │
└─────────────────────────────────────────────┘
```

**Bounded by:** Highway 22 • Highway 6 • McLennan County Line

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/williambevans/bosqueTriangle.git
cd bosqueTriangle

# Install dependencies
pip install -r requirements.txt

# Optional: Install Playwright for browser scraping
playwright install chromium
```

### Run Test Scraper

```bash
# Test with small area (~50 parcels)
python test_scraper.py
```

**Output:** Creates `docs/data/parcels.geojson` for GitHub Pages

### Launch Web Interface

**Option 1: GitHub Pages (Recommended)**

🌐 **Live Site:** https://williambevans.github.io/bosqueTriangle/

To update data:
```bash
python scraper.py               # Generate new data
git add docs/data/parcels.geojson
git commit -m "Update parcel data"
git push                        # Site updates in ~2 min
```

**Option 2: Local Flask Server**

```bash
python web_server.py
# Open: http://localhost:5000
```

### Full Scrape

```bash
# Extract all parcels in target triangle
python scraper.py
```

---

## 📂 Project Structure

```
bosqueTriangle/
├── 📊 scraper.py              # Main ArcGIS REST scraper
├── 🧪 test_scraper.py         # Small area test
├── 🔍 discover_endpoint.py    # Endpoint auto-detection
├── 🌐 web_server.py           # Flask development server
├── 🎭 browser_scraper.py      # Playwright fallback
├── ⚙️  config.json             # Configuration & polygon
├── 📦 requirements.txt        # Python dependencies
│
├── 📄 docs/                   # GitHub Pages site
│   ├── index.html            # Interactive map interface
│   ├── _config.yml           # Pages configuration
│   └── data/
│       ├── parcels.geojson   # Generated parcel data
│       └── infrastructure.geojson  # Phases, POIs, substations
│
└── 📁 output/                 # Timestamped exports
    ├── bosque_parcels_*.json
    ├── bosque_parcels_*.geojson
    └── bosque_plat_summary_*.csv
```

---

## 🗺️ Web Interface

<div align="center">

### Professional Investment Presentation Design

![Dark Theme](https://img.shields.io/badge/Theme-Dark%20%231a1a1a-black?style=for-the-badge)
![Gold Accents](https://img.shields.io/badge/Accents-Gold%20%23c4a661-yellow?style=for-the-badge)
![Mobile Ready](https://img.shields.io/badge/Mobile-Responsive-blue?style=for-the-badge)

</div>

**Features:**
- 🎨 H.H.H. Holdings branded header
- 📍 **Development Phases** (Phase 1, 2, 4) with capacity labels
- ⚡ **POI Markers** (orange circles) showing power generation points
- 💎 **Substations** (green diamonds) - Clifton Sub, Whitney Sub
- 📦 **Central Collectors** (dashed squares) - Proposed 345kV
- 🔌 **Transmission Lines** (cyan/orange) - 345kV and 138kV
- 📊 **Progress Bars** - Solar Developed, Active Leases, Open Land
- 🔍 **Click parcels** for owner, acreage, status details

**Color Coding:**
- 🟨 **Gold** - Solar developed parcels
- ⬜ **Gray** - Active leases
- ⬛ **Dark Gray** - Open land

---

## 📊 Data Model

### Parcel Object

```json
{
  "parcel_id": "R12345",
  "owner": {
    "name": "John Smith",
    "mailing_address": "123 Main St, Dallas, TX 75201"
  },
  "situs_address": "456 County Road 789, Clifton, TX",
  "legal_description": "ABSTRACT 123, SURVEY 45, ACRES 10.5",
  "subdivision": "Clifton Ranch Estates",
  "acreage": 10.5,
  "market_value": "125000",
  "status": "open",
  "geometry": { "type": "Polygon", "coordinates": [[...]] }
}
```

### Status Values

| Status | Description | Map Color |
|--------|-------------|-----------|
| `solar_developed` | Owned by solar/energy company | 🟨 Gold (#c4a661) |
| `active_lease` | Lease or option agreement | ⬜ Gray (#808080) |
| `open` | Available land | ⬛ Dark Gray (#404040) |

### Infrastructure Features

```json
{
  "phases": ["PHASE 1: 3342 MW", "PHASE 2: 3342 MW", "PHASE 4: 2705 MW"],
  "pois": ["POI-1: 3342V", "POI-2: 345kV", "POI-3: 345kV", "POI-4: 138kV"],
  "substations": ["CLIFTON SUB: 138kV", "WHITNEY SUB: 345kV/138kV"],
  "collectors": ["CENTRAL COLLECTOR: Proposed 345kV"],
  "transmission": ["345kV Lines", "138kV Lines"]
}
```

---

## 🌐 Data Sources

### Primary: TNRIS Statewide Parcels

**URL:** https://feature.stratmap.tnris.org/arcgis/rest/services/Parcels/StratMap_Parcels/MapServer/0

- **Type:** ArcGIS REST API
- **Coverage:** Statewide Texas parcels
- **Update:** Quarterly
- **Format:** GeoJSON

### Fallback: Bosque CAD

**URL:** https://esearch.bosquecad.com/

- **Type:** Web scraper (Playwright)
- **Note:** Requires configuration

---

## ⚙️ Configuration

Edit `config.json` to customize:

```json
{
  "target_polygon": {
    "type": "Polygon",
    "coordinates": [[[lon, lat], ...]]
  },
  "scraper_settings": {
    "rate_limit_seconds": 0.5,
    "max_records_per_request": 1000,
    "retry_attempts": 3,
    "timeout_seconds": 30
  },
  "field_mappings": {
    "parcel_id": ["PARCEL_ID", "PIN", "GEO_ID"],
    "owner": ["OWNER", "OWNER_NAME"],
    "acreage": ["ACRES", "GIS_ACRES"]
  }
}
```

---

## 🔧 Advanced Usage

### Discover Alternative Endpoints

```bash
python discover_endpoint.py
```

Finds alternative GIS service endpoints automatically.

### Custom Polygon Area

```python
# test_scraper.py
test_polygon = {
    "type": "Polygon",
    "coordinates": [
        [[-97.58, 31.78], [-97.56, 31.78],
         [-97.56, 31.80], [-97.58, 31.80],
         [-97.58, 31.78]]
    ]
}
```

### Load in QGIS

1. Open QGIS
2. **Layer → Add Layer → Add Vector Layer**
3. Select `output/bosque_parcels_*.geojson`
4. Style by `status` field (solar/lease/open)
5. Add basemap for context

---

## 📊 Use Cases

<table>
<tr>
<td width="50%">

### 🏭 Energy Development
- Track solar farm development
- Monitor leasing activity
- Identify open land clusters
- Phase planning analysis

</td>
<td width="50%">

### 🏢 Real Estate Intelligence
- Data center corridor analysis
- Transmission easement mapping
- Land aggregation opportunities
- Ownership pattern research

</td>
</tr>
<tr>
<td width="50%">

### 📈 Investment Due Diligence
- Property research
- Market analysis
- Competitive landscape
- Strategic acquisitions

</td>
<td width="50%">

### 🔍 Public Records Access
- County transparency
- Development tracking
- Parcel ownership history
- Zoning & land use

</td>
</tr>
</table>

---

## 🌟 GitHub Pages Deployment

### Setup (One Time)

1. **Enable GitHub Pages**
   - Go to **Settings → Pages**
   - Source: **Deploy from a branch**
   - Branch: **`main`**
   - Folder: **`/docs`**
   - Click **Save**

2. **Generate Initial Data**
   ```bash
   python test_scraper.py
   ```

3. **Deploy**
   ```bash
   git add docs/data/parcels.geojson
   git commit -m "Add parcel data"
   git push
   ```

4. **Access Site** (within 2 minutes)
   ```
   https://[username].github.io/bosqueTriangle/
   ```

### Update Data

```bash
# Re-run scraper (updates docs/data/parcels.geojson)
python scraper.py

# Deploy update
git add docs/data/parcels.geojson
git commit -m "Update parcel data - $(date +%Y-%m-%d)"
git push
```

**See:** [GITHUB_PAGES.md](GITHUB_PAGES.md) for complete guide

---

## 🛠️ Development

### Run Tests

```bash
# Small area test (~50 parcels)
python test_scraper.py

# Verify outputs
ls -lh output/
ls -lh docs/data/
```

### Adding Data Sources

1. Add source to `config.json`
2. Update `field_mappings` if needed
3. Test with `test_scraper.py`
4. Run full scrape

---

## 🔒 Rate Limiting & Ethics

- ✅ **Rate limit:** 0.5s between requests
- ✅ **Retry logic:** 3 attempts with exponential backoff
- ✅ **Public data only:** All sources are public records
- ✅ **Respectful scraping:** Adheres to ToS and reasonable use

---

## 🚦 Troubleshooting

### No data returned

```bash
python discover_endpoint.py  # Test connectivity
```

### Web interface shows demo data

```bash
python test_scraper.py       # Generate real data
```

### Import errors

```bash
pip install -r requirements.txt --upgrade
```

### Playwright issues

```bash
playwright install --force chromium
```

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Records per request | ~1,000 |
| Requests per second | ~2 (with rate limiting) |
| Full scrape time | 5-10 minutes |
| GitHub Pages load | < 2 seconds globally |
| Cost | $0 (free hosting) |

---

## 📋 Requirements

- **Python:** 3.9+
- **Libraries:** requests, shapely, pandas, flask, playwright
- **Optional:** QGIS for advanced visualization
- **Hosting:** GitHub Pages (free, unlimited views)

---

## 📝 License

This project is for authorized real estate research and analysis. All parcel data remains property of respective county appraisal districts and the State of Texas.

---

## 📧 Contact

<div align="center">

### H.H.H. Holdings

**For investment inquiries:**
📧 holdings@hhh.com

---

**Built for Bevans Real Estate**
*Property research and data center corridor analysis in Central Texas*

[![GitHub](https://img.shields.io/badge/GitHub-bosqueTriangle-black?logo=github)](https://github.com/williambevans/bosqueTriangle)
[![Website](https://img.shields.io/badge/Website-Live%20Demo-blue)](https://williambevans.github.io/bosqueTriangle/)

</div>

---

<div align="center">

**Built with ❤️ for strategic land acquisition and transparency in public records**

*Track development • Identify opportunities • Make informed decisions*

</div>
