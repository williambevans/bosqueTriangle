#!/usr/bin/env python3
"""
Discover ArcGIS REST endpoints for Bosque County CAD
Attempts to find working GIS service endpoints automatically
"""

import requests
import json
import sys
from typing import List, Dict, Optional
from urllib.parse import urljoin


class EndpointDiscovery:
    """Auto-detect CAD GIS endpoints"""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def test_endpoint(self, url: str) -> Optional[Dict]:
        """Test if an endpoint is valid and return its metadata"""
        try:
            # Try with f=json parameter
            response = self.session.get(
                url,
                params={'f': 'json'},
                timeout=self.timeout
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    # Check if it's a valid ArcGIS service
                    if 'type' in data or 'layers' in data or 'tables' in data:
                        return data
                except json.JSONDecodeError:
                    pass

        except requests.RequestException as e:
            print(f"  Error testing {url}: {str(e)[:50]}")

        return None

    def discover_common_paths(self) -> List[Dict]:
        """Try common ArcGIS REST endpoint patterns"""
        common_paths = [
            '/arcgis/rest/services',
            '/rest/services',
            '/gis/rest/services',
            '/arcgis/services',
            '/ArcGIS/rest/services',
        ]

        found_services = []

        print("Discovering ArcGIS REST services...")
        for path in common_paths:
            url = self.base_url + path
            print(f"Testing: {url}")

            result = self.test_endpoint(url)
            if result:
                print(f"  ✓ Found service catalog")
                found_services.append({
                    'url': url,
                    'type': 'catalog',
                    'metadata': result
                })

                # Try to enumerate services in the catalog
                if 'services' in result:
                    for service in result['services']:
                        service_name = service.get('name', '')
                        service_type = service.get('type', 'MapServer')
                        service_url = f"{url}/{service_name}/{service_type}"

                        print(f"  Testing service: {service_url}")
                        service_data = self.test_endpoint(service_url)

                        if service_data:
                            found_services.append({
                                'url': service_url,
                                'type': 'service',
                                'name': service_name,
                                'service_type': service_type,
                                'metadata': service_data
                            })

                            # Check for layers
                            if 'layers' in service_data:
                                print(f"    Found {len(service_data['layers'])} layers")
                                for layer in service_data['layers']:
                                    layer_id = layer.get('id')
                                    layer_name = layer.get('name')
                                    print(f"      - Layer {layer_id}: {layer_name}")

        return found_services

    def discover_parcel_layers(self, services: List[Dict]) -> List[Dict]:
        """Find layers that likely contain parcel data"""
        parcel_keywords = ['parcel', 'property', 'tax', 'cadastral', 'land', 'lot']
        parcel_layers = []

        print("\nSearching for parcel layers...")

        for service in services:
            if service['type'] != 'service':
                continue

            metadata = service['metadata']
            if 'layers' not in metadata:
                continue

            for layer in metadata['layers']:
                layer_id = layer.get('id')
                layer_name = layer.get('name', '').lower()

                # Check if layer name contains parcel-related keywords
                if any(keyword in layer_name for keyword in parcel_keywords):
                    layer_url = f"{service['url']}/{layer_id}"
                    print(f"  ✓ Found potential parcel layer: {layer_name}")
                    print(f"    URL: {layer_url}")

                    # Get detailed layer info
                    layer_info = self.test_endpoint(layer_url)

                    if layer_info:
                        fields = layer_info.get('fields', [])
                        field_names = [f['name'] for f in fields]

                        print(f"    Fields: {', '.join(field_names[:10])}")
                        if len(field_names) > 10:
                            print(f"    ... and {len(field_names) - 10} more")

                        parcel_layers.append({
                            'url': layer_url,
                            'name': layer['name'],
                            'id': layer_id,
                            'service': service['name'],
                            'fields': field_names,
                            'metadata': layer_info
                        })

        return parcel_layers


def main():
    """Main discovery process"""

    # Primary source (TNRIS)
    print("=" * 70)
    print("PRIMARY SOURCE: TNRIS Statewide Parcels")
    print("=" * 70)

    tnris_url = "https://feature.stratmap.tnris.org"
    tnris_discovery = EndpointDiscovery(tnris_url)

    # Test the known TNRIS endpoint
    known_endpoint = "https://feature.stratmap.tnris.org/arcgis/rest/services/Parcels/StratMap_Parcels/MapServer/0"
    print(f"\nTesting known TNRIS endpoint: {known_endpoint}")

    result = tnris_discovery.test_endpoint(known_endpoint)
    if result:
        print("✓ TNRIS endpoint is accessible")
        print(f"  Service: {result.get('name', 'Unknown')}")
        print(f"  Type: {result.get('type', 'Unknown')}")
        if 'fields' in result:
            print(f"  Fields: {len(result['fields'])} fields available")
    else:
        print("✗ TNRIS endpoint not accessible")

    # Try Bosque CAD
    print("\n" + "=" * 70)
    print("FALLBACK SOURCE: Bosque CAD")
    print("=" * 70)

    bosque_cad_url = "https://esearch.bosquecad.com"
    bosque_discovery = EndpointDiscovery(bosque_cad_url)

    services = bosque_discovery.discover_common_paths()

    if services:
        print(f"\n✓ Found {len(services)} services")
        parcel_layers = bosque_discovery.discover_parcel_layers(services)

        if parcel_layers:
            print(f"\n✓ Found {len(parcel_layers)} parcel layers")

            # Save results
            output_file = "discovered_endpoints.json"
            with open(output_file, 'w') as f:
                json.dump({
                    'tnris': {
                        'url': known_endpoint,
                        'status': 'accessible' if result else 'not accessible'
                    },
                    'bosque_cad': {
                        'services': services,
                        'parcel_layers': parcel_layers
                    }
                }, f, indent=2)

            print(f"\n✓ Results saved to {output_file}")
        else:
            print("\n✗ No parcel layers found")
    else:
        print("\n✗ No ArcGIS services found at Bosque CAD")
        print("Will need to use browser_scraper.py for web UI scraping")

    return 0


if __name__ == '__main__':
    sys.exit(main())
