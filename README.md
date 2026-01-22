# Bosque County Parcel Scraper

**Central Texas Integrated Energy & Compute Zone**

Professional-grade Python scraper and web visualization for Bosque County, Texas parcel data. Extracts parcels within the triangle bounded by Highway 22, Highway 6, and the McLennan County line. Tracks solar development status, active leases, and open land for strategic real estate analysis.

## Overview

This project provides:
- **Automated Parcel Extraction** from TNRIS Statewide Parcels ArcGIS REST API
- **Solar Development Tracking** (solar developed, active leases, open land)
- **Interactive Web Map** with dark theme and gold accents matching investment presentation style
- **Progress Visualization** showing land development status
- **Multiple Export Formats** (JSON, GeoJSON, CSV)
- **Subdivision Grouping** for plat-level analysis

## Target Area

**Coordinates (WGS84):**
- Clifton (Southwest): -97.5769, 31.7823
- Lake Whitney (North): -97.3618, 31.9508
- McLennan County/Hwy 6 (Southeast): -97.2891, 31.7234

**Total Coverage:** ~130,000 acres in Bosque County, TX

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/williambevans/bosqueTriangle.git
cd bosqueTriangle

# Install Python dependencies
pip install -r requirements.txt

# Install browser for Playwright (fallback only)
playwright install chromium
```

### Run Small Test

Test with a limited area first:

```bash
python test_scraper.py
```

This fetches 10-50 parcels around Clifton for validation.

### Full Scrape

Extract all parcels in target triangle:

```bash
python scraper.py
```

Output files saved to `output/` directory:
- `bosque_parcels_YYYYMMDD_HHMMSS.json` - Full nested data
- `bosque_parcels_YYYYMMDD_HHMMSS.geojson` - For QGIS/mapping
- `bosque_plat_summary_YYYYMMDD_HHMMSS.csv` - Spreadsheet summary

### Launch Web Viewer

**Option 1: GitHub Pages (Recommended)**

The site is automatically deployed to GitHub Pages at:
**https://williambevans.github.io/bosqueTriangle/**

To update the data:
1. Run `python test_scraper.py` or `python scraper.py`
2. Commit and push the generated `docs/data/parcels.geojson`
3. Site updates automatically

**Option 2: Local Flask Server**

View locally with Flask:

```bash
python web_server.py
```

Open browser to: **http://localhost:5000**

## Project Structure

```
bosqueTriangle/
├── config.json              # Configuration and target polygon
├── scraper.py              # Main ArcGIS REST scraper
├── test_scraper.py         # Small area test scraper
├── discover_endpoint.py    # Auto-detect GIS endpoints
├── browser_scraper.py      # Playwright fallback (template)
├── web_server.py           # Flask web server
├── web/
│   └── index.html         # Interactive map viewer
├── output/                # Generated data files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Data Model

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
  "geometry": {
    "type": "Polygon",
    "coordinates": [[...]]
  }
}
```

### Status Values

- **`solar_developed`** - Owned by solar/energy company
- **`active_lease`** - Lease or option mentioned in legal description
- **`open`** - Available land (no solar development or lease)

### Plat Object

```json
{
  "name": "Clifton Ranch Estates",
  "total_parcels": 47,
  "total_acreage": 523.8,
  "solar_developed": 2,
  "active_leases": 8,
  "open_land": 37,
  "parcels": [...]
}
```

## Data Sources

### Primary: TNRIS Statewide Parcels

**URL:** https://feature.stratmap.tnris.org/arcgis/rest/services/Parcels/StratMap_Parcels/MapServer/0

**Type:** ArcGIS REST API
**Coverage:** Statewide Texas parcels
**Update Frequency:** Quarterly

### Fallback: Bosque CAD

**URL:** https://esearch.bosquecad.com/

**Type:** Web scraper (requires configuration)
**Note:** Use if ArcGIS REST API unavailable

## Field Mappings

The scraper handles variations in field names:

| Standard Field | Variations |
|---------------|-----------|
| Parcel ID | `PARCEL_ID`, `ParcelID`, `PIN`, `GEO_ID`, `PROP_ID` |
| Owner | `OWNER`, `OWNER_NAME`, `OwnerName` |
| Acreage | `ACRES`, `Acreage`, `GIS_ACRES` |
| Subdivision | `SUBDIV`, `SUBDIVISION`, `SUB_NAME`, `PLAT_NAME` |
| Address | `SITUS_ADDR`, `SITUS_ADDRESS`, `SitusAddress` |

## ArcGIS Query Pattern

```python
params = {
    'where': '1=1',
    'geometry': json.dumps(polygon),
    'geometryType': 'esriGeometryPolygon',
    'spatialRel': 'esriSpatialRelIntersects',
    'inSR': '4326',
    'outSR': '4326',
    'outFields': '*',
    'returnGeometry': 'true',
    'f': 'geojson',
    'resultOffset': 0,
    'resultRecordCount': 1000
}
```

## GitHub Pages Deployment

This project is configured for automatic deployment to GitHub Pages.

### Setup

1. **Enable GitHub Pages** in your repository settings:
   - Go to Settings → Pages
   - Source: Deploy from branch
   - Branch: `main` (or your default branch)
   - Folder: `/docs`
   - Save

2. **Run the scraper** to generate data:
   ```bash
   python test_scraper.py  # or python scraper.py
   ```

3. **Commit and push** the generated data:
   ```bash
   git add docs/data/parcels.geojson
   git commit -m "Add parcel data"
   git push
   ```

4. **Access your site**:
   - URL: `https://[username].github.io/bosqueTriangle/`
   - Example: https://williambevans.github.io/bosqueTriangle/

### Updating Data

To refresh the map with new parcel data:

```bash
# Re-run scraper
python scraper.py

# Push updates
git add docs/data/parcels.geojson
git commit -m "Update parcel data"
git push
```

Site updates automatically within 1-2 minutes.

## Configuration

Edit `config.json` to customize:

- **Target polygon coordinates**
- **Data source URLs**
- **Rate limiting** (default: 0.5s between requests)
- **Pagination** (default: 1000 records per request)
- **Field mappings** for different data sources

## Web Interface

### Styling

The web interface matches professional investment presentation design:

- **Dark theme** (#1a1a1a background)
- **Gold accents** (#c4a661) for emphasis
- **Serif typography** (Georgia) for elegance
- **Progress bars** showing development status
- **Interactive map** with parcel details on click

### Features

- Real-time statistics display
- Color-coded parcels by status:
  - **Gold** - Solar developed
  - **Gray** - Active leases
  - **Dark gray** - Open land
- Click parcels for detailed information
- Responsive design for mobile/tablet

## Use Cases

This tool supports:

1. **Data Center Corridor Analysis** - Identify ownership patterns along transmission corridors
2. **Solar Development Tracking** - Monitor solar farm development and leasing activity
3. **Land Aggregation** - Find clusters of open land for acquisition
4. **Transmission Easements** - Map potential easement routes
5. **County Transparency** - Public record access and analysis
6. **Investment Due Diligence** - Property research for real estate transactions

## Advanced Usage

### Discover New Endpoints

Find alternative GIS service endpoints:

```bash
python discover_endpoint.py
```

### Custom Polygon

Edit `config.json` to change target area:

```json
{
  "target_polygon": {
    "type": "Polygon",
    "coordinates": [
      [
        [-97.58, 31.78],
        [-97.56, 31.80],
        [-97.54, 31.78],
        [-97.58, 31.78]
      ]
    ]
  }
}
```

### Load in QGIS

1. Open QGIS
2. Layer → Add Layer → Add Vector Layer
3. Select `output/bosque_parcels_*.geojson`
4. Style by `status` field
5. Add basemap for context

## Rate Limiting & Ethics

- **Rate limit:** 0.5s between requests (configurable)
- **Retry logic:** 3 attempts with exponential backoff
- **Public data only:** All sources are public records
- **Respectful scraping:** Adheres to reasonable use policies

## Troubleshooting

### No data returned

```bash
# Test endpoint connectivity
python discover_endpoint.py
```

### Import errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Web interface shows demo data

```bash
# Run scraper first to generate data
python test_scraper.py
python web_server.py
```

### Playwright browser issues

```bash
# Reinstall browser
playwright install --force chromium
```

## Development

### Running Tests

```bash
# Test small area (10-50 parcels)
python test_scraper.py

# Verify outputs exist
ls -lh output/
```

### Adding New Data Sources

1. Add source to `config.json` under `data_sources`
2. Update field mappings if needed
3. Test with `test_scraper.py`
4. Run full scrape with `scraper.py`

## Technical Details

**Language:** Python 3.9+
**REST API:** Requests library
**GIS:** Shapely for spatial operations
**Web:** Flask + Leaflet.js
**Browser Automation:** Playwright (optional)

**Performance:**
- ~1000 parcels per request
- ~2 requests per second (with rate limiting)
- Full scrape completes in 5-10 minutes

## License

This project is for authorized real estate research and analysis. All parcel data remains property of respective county appraisal districts and the State of Texas.

## Contact

**H.H.H. Holdings**
For investment inquiries: holdings@hhh.com

---

**For Bevans Real Estate** - Property research and data center corridor analysis in Central Texas.

Built with ❤️ for strategic land acquisition and transparency in public records.
