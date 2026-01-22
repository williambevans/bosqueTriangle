#!/usr/bin/env python3
"""
Test scraper with small area to validate functionality
"""

import json
from scraper import ParcelScraper
from datetime import datetime
from pathlib import Path


def test_small_area():
    """Test with a smaller polygon around Clifton area"""

    # Create smaller test polygon (just around Clifton)
    test_polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [-97.58, 31.78],
                [-97.56, 31.78],
                [-97.56, 31.80],
                [-97.58, 31.80],
                [-97.58, 31.78]
            ]
        ]
    }

    print("Testing with small area around Clifton...")
    print("This will fetch ~10-50 parcels for validation\n")

    scraper = ParcelScraper()

    # Override target polygon for testing
    scraper.config['target_polygon'] = test_polygon

    # Run scrape
    if scraper.scrape():
        scraper.print_statistics()

        # Export test data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        test_json = output_dir / f"test_parcels_{timestamp}.json"
        test_geojson = output_dir / f"test_parcels_{timestamp}.geojson"

        scraper.export_json(str(test_json))
        scraper.export_geojson(str(test_geojson))

        # Export for GitHub Pages
        github_pages_dir = Path("docs/data")
        github_pages_dir.mkdir(parents=True, exist_ok=True)
        github_pages_geojson = github_pages_dir / "parcels.geojson"

        scraper.export_geojson(str(github_pages_geojson))
        print(f"✓ Exported for GitHub Pages: {github_pages_geojson}")

        print(f"\n✓ Test complete - check {test_geojson} in QGIS to verify")
        return 0
    else:
        print("Test failed")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(test_small_area())
