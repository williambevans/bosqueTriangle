#!/usr/bin/env python3
"""
Bosque County Parcel Scraper
Extracts parcel data from ArcGIS REST services within target triangle area
Tracks solar development status and lease information
"""

import json
import time
import sys
import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import csv


class ParcelScraper:
    """Main scraper for ArcGIS REST parcel data"""

    def __init__(self, config_path: str = "config.json"):
        """Initialize scraper with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        self.rate_limit = self.config['scraper_settings']['rate_limit_seconds']
        self.max_records = self.config['scraper_settings']['max_records_per_request']
        self.timeout = self.config['scraper_settings']['timeout_seconds']
        self.retry_attempts = self.config['scraper_settings']['retry_attempts']

        self.parcels = []
        self.plats = {}
        self.stats = {
            'total_parcels': 0,
            'solar_developed': 0,
            'active_leases': 0,
            'open_land': 0,
            'total_acreage': 0.0
        }

    def get_field_value(self, properties: Dict, field_type: str) -> Optional[str]:
        """Get field value using field mapping variations"""
        field_variations = self.config['field_mappings'].get(field_type, [])

        for field_name in field_variations:
            if field_name in properties:
                value = properties[field_name]
                return str(value) if value is not None else None

        return None

    def query_arcgis_layer(self, url: str, geometry: Dict, offset: int = 0) -> Optional[Dict]:
        """Query ArcGIS REST endpoint with spatial filter"""

        # Build query parameters
        params = {
            'where': '1=1',
            'geometry': json.dumps(geometry),
            'geometryType': 'esriGeometryPolygon',
            'spatialRel': 'esriSpatialRelIntersects',
            'inSR': '4326',
            'outSR': '4326',
            'outFields': '*',
            'returnGeometry': 'true',
            'f': 'geojson',
            'resultOffset': offset,
            'resultRecordCount': self.max_records
        }

        for attempt in range(self.retry_attempts):
            try:
                response = self.session.get(
                    f"{url}/query",
                    params=params,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"  HTTP {response.status_code}: {response.text[:100]}")

            except requests.RequestException as e:
                print(f"  Attempt {attempt + 1} failed: {str(e)[:100]}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)

        return None

    def determine_parcel_status(self, properties: Dict) -> str:
        """Determine if parcel is solar developed, leased, or open"""

        # Check owner name for solar companies
        owner = self.get_field_value(properties, 'owner') or ''
        owner_lower = owner.lower()

        solar_keywords = ['solar', 'energy', 'renewable', 'power', 'electric utility']
        lease_keywords = ['lease', 'option']

        # Check if owned by solar company
        if any(keyword in owner_lower for keyword in solar_keywords):
            return 'solar_developed'

        # Check legal description for lease mentions
        legal_desc = self.get_field_value(properties, 'legal_description') or ''
        if any(keyword in legal_desc.lower() for keyword in lease_keywords):
            return 'active_lease'

        # Otherwise it's open land
        return 'open'

    def parse_parcel(self, feature: Dict) -> Dict:
        """Parse GeoJSON feature into parcel object"""
        properties = feature.get('properties', {})
        geometry = feature.get('geometry')

        # Extract fields using mapping
        parcel_id = self.get_field_value(properties, 'parcel_id') or 'UNKNOWN'
        owner = self.get_field_value(properties, 'owner') or 'Unknown Owner'
        acreage_str = self.get_field_value(properties, 'acreage') or '0'

        try:
            acreage = float(acreage_str)
        except (ValueError, TypeError):
            acreage = 0.0

        subdivision = self.get_field_value(properties, 'subdivision') or 'Unplatted'
        situs_address = self.get_field_value(properties, 'situs_address') or ''
        legal_desc = self.get_field_value(properties, 'legal_description') or ''
        market_value = self.get_field_value(properties, 'market_value') or '0'
        owner_address = self.get_field_value(properties, 'owner_address') or ''

        # Determine development status
        status = self.determine_parcel_status(properties)

        parcel = {
            'parcel_id': parcel_id,
            'owner': {
                'name': owner,
                'mailing_address': owner_address
            },
            'situs_address': situs_address,
            'legal_description': legal_desc,
            'subdivision': subdivision,
            'acreage': acreage,
            'market_value': market_value,
            'status': status,  # 'solar_developed', 'active_lease', or 'open'
            'geometry': geometry,
            'raw_properties': properties
        }

        return parcel

    def group_by_plat(self):
        """Group parcels by subdivision/plat"""
        self.plats = {}

        for parcel in self.parcels:
            plat_name = parcel['subdivision']

            if plat_name not in self.plats:
                self.plats[plat_name] = {
                    'name': plat_name,
                    'total_parcels': 0,
                    'total_acreage': 0.0,
                    'solar_developed': 0,
                    'active_leases': 0,
                    'open_land': 0,
                    'parcels': []
                }

            self.plats[plat_name]['parcels'].append(parcel)
            self.plats[plat_name]['total_parcels'] += 1
            self.plats[plat_name]['total_acreage'] += parcel['acreage']

            # Update status counts
            status = parcel['status']
            if status == 'solar_developed':
                self.plats[plat_name]['solar_developed'] += 1
            elif status == 'active_lease':
                self.plats[plat_name]['active_leases'] += 1
            else:
                self.plats[plat_name]['open_land'] += 1

    def calculate_statistics(self):
        """Calculate overall statistics"""
        self.stats = {
            'total_parcels': len(self.parcels),
            'solar_developed': 0,
            'active_leases': 0,
            'open_land': 0,
            'total_acreage': 0.0,
            'solar_acreage': 0.0,
            'lease_acreage': 0.0,
            'open_acreage': 0.0
        }

        for parcel in self.parcels:
            self.stats['total_acreage'] += parcel['acreage']

            status = parcel['status']
            if status == 'solar_developed':
                self.stats['solar_developed'] += 1
                self.stats['solar_acreage'] += parcel['acreage']
            elif status == 'active_lease':
                self.stats['active_leases'] += 1
                self.stats['lease_acreage'] += parcel['acreage']
            else:
                self.stats['open_land'] += 1
                self.stats['open_acreage'] += parcel['acreage']

    def scrape(self, endpoint_url: str = None) -> bool:
        """Main scraping process"""

        if endpoint_url is None:
            endpoint_url = self.config['data_sources']['primary']['url']

        print(f"Scraping parcels from: {endpoint_url}")
        print(f"Target area: {self.config['target_polygon']['description']}")

        target_geometry = self.config['target_polygon']

        offset = 0
        total_fetched = 0

        while True:
            print(f"\nFetching records {offset} to {offset + self.max_records}...")

            result = self.query_arcgis_layer(endpoint_url, target_geometry, offset)

            if result is None:
                print("Failed to fetch data")
                return False

            features = result.get('features', [])
            if not features:
                print("No more features to fetch")
                break

            print(f"  Got {len(features)} features")

            # Parse features
            for feature in features:
                try:
                    parcel = self.parse_parcel(feature)
                    self.parcels.append(parcel)
                    total_fetched += 1
                except Exception as e:
                    print(f"  Error parsing feature: {str(e)[:100]}")

            # Check if we got fewer records than requested (last page)
            if len(features) < self.max_records:
                print("Reached last page")
                break

            offset += self.max_records

            # Rate limiting
            time.sleep(self.rate_limit)

        print(f"\n✓ Scraped {total_fetched} parcels total")

        # Group and calculate stats
        print("Grouping by subdivision...")
        self.group_by_plat()

        print("Calculating statistics...")
        self.calculate_statistics()

        return True

    def export_json(self, output_path: str):
        """Export full nested JSON"""
        data = {
            'metadata': {
                'scraped_at': datetime.now().isoformat(),
                'target_area': self.config['target_polygon']['description'],
                'source': self.config['data_sources']['primary']['name']
            },
            'statistics': self.stats,
            'plats': list(self.plats.values())
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"✓ Exported JSON: {output_path}")

    def export_geojson(self, output_path: str):
        """Export GeoJSON for mapping"""
        features = []

        for parcel in self.parcels:
            feature = {
                'type': 'Feature',
                'properties': {
                    'parcel_id': parcel['parcel_id'],
                    'owner': parcel['owner']['name'],
                    'subdivision': parcel['subdivision'],
                    'acreage': parcel['acreage'],
                    'status': parcel['status'],
                    'situs_address': parcel['situs_address']
                },
                'geometry': parcel['geometry']
            }
            features.append(feature)

        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }

        with open(output_path, 'w') as f:
            json.dump(geojson, f)

        print(f"✓ Exported GeoJSON: {output_path}")

    def export_csv(self, output_path: str):
        """Export CSV summary by plat"""
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Subdivision',
                'Total Parcels',
                'Total Acres',
                'Solar Developed',
                'Active Leases',
                'Open Land',
                'Solar %',
                'Lease %',
                'Open %'
            ])

            for plat in self.plats.values():
                total = plat['total_parcels']
                solar_pct = (plat['solar_developed'] / total * 100) if total > 0 else 0
                lease_pct = (plat['active_leases'] / total * 100) if total > 0 else 0
                open_pct = (plat['open_land'] / total * 100) if total > 0 else 0

                writer.writerow([
                    plat['name'],
                    total,
                    f"{plat['total_acreage']:.2f}",
                    plat['solar_developed'],
                    plat['active_leases'],
                    plat['open_land'],
                    f"{solar_pct:.1f}%",
                    f"{lease_pct:.1f}%",
                    f"{open_pct:.1f}%"
                ])

        print(f"✓ Exported CSV: {output_path}")

    def print_statistics(self):
        """Print summary statistics"""
        print("\n" + "=" * 70)
        print("SCRAPING RESULTS")
        print("=" * 70)
        print(f"Total Parcels:    {self.stats['total_parcels']:,}")
        print(f"Total Acreage:    {self.stats['total_acreage']:,.2f} acres")
        print()
        print(f"Solar Developed:  {self.stats['solar_developed']:,} parcels ({self.stats['solar_acreage']:,.2f} acres)")
        print(f"Active Leases:    {self.stats['active_leases']:,} parcels ({self.stats['lease_acreage']:,.2f} acres)")
        print(f"Open Land:        {self.stats['open_land']:,} parcels ({self.stats['open_acreage']:,.2f} acres)")
        print()

        if self.stats['total_parcels'] > 0:
            solar_pct = self.stats['solar_developed'] / self.stats['total_parcels'] * 100
            lease_pct = self.stats['active_leases'] / self.stats['total_parcels'] * 100
            open_pct = self.stats['open_land'] / self.stats['total_parcels'] * 100
            print(f"Solar %:          {solar_pct:.1f}%")
            print(f"Lease %:          {lease_pct:.1f}%")
            print(f"Open %:           {open_pct:.1f}%")

        print(f"\nSubdivisions:     {len(self.plats)}")
        print("=" * 70)


def main():
    """Main execution"""
    print("Bosque County Parcel Scraper")
    print("=" * 70)

    scraper = ParcelScraper()

    # Run the scrape
    if not scraper.scrape():
        print("Scraping failed")
        return 1

    # Print results
    scraper.print_statistics()

    # Export data
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / f"bosque_parcels_{timestamp}.json"
    geojson_path = output_dir / f"bosque_parcels_{timestamp}.geojson"
    csv_path = output_dir / f"bosque_plat_summary_{timestamp}.csv"

    print("\nExporting data...")
    scraper.export_json(str(json_path))
    scraper.export_geojson(str(geojson_path))
    scraper.export_csv(str(csv_path))

    print("\n✓ Complete!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
