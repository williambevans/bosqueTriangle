#!/usr/bin/env python3
"""
Simple web server to display parcel map and statistics
"""

from flask import Flask, jsonify, send_from_directory
from pathlib import Path
import json
import glob
import os

app = Flask(__name__, static_folder='web', static_url_path='')

# Get the most recent GeoJSON file
def get_latest_geojson():
    """Find the most recent parcel GeoJSON file"""
    output_dir = Path('output')

    if not output_dir.exists():
        return None

    geojson_files = list(output_dir.glob('bosque_parcels_*.geojson'))

    if not geojson_files:
        geojson_files = list(output_dir.glob('test_parcels_*.geojson'))

    if not geojson_files:
        return None

    # Get most recent file
    latest_file = max(geojson_files, key=lambda p: p.stat().st_mtime)
    return latest_file


@app.route('/')
def index():
    """Serve main page"""
    return send_from_directory('web', 'index.html')


@app.route('/api/parcels')
def get_parcels():
    """API endpoint for parcel data"""
    geojson_file = get_latest_geojson()

    if geojson_file is None:
        return jsonify({
            'error': 'No parcel data available',
            'message': 'Run scraper.py or test_scraper.py first to generate data'
        }), 404

    with open(geojson_file, 'r') as f:
        data = json.load(f)

    return jsonify(data)


@app.route('/api/stats')
def get_stats():
    """API endpoint for statistics"""
    output_dir = Path('output')

    if not output_dir.exists():
        return jsonify({'error': 'No data available'}), 404

    json_files = list(output_dir.glob('bosque_parcels_*.json'))

    if not json_files:
        json_files = list(output_dir.glob('test_parcels_*.json'))

    if not json_files:
        return jsonify({'error': 'No statistics available'}), 404

    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)

    with open(latest_file, 'r') as f:
        data = json.load(f)

    return jsonify(data.get('statistics', {}))


def main():
    """Start the web server"""
    print("=" * 70)
    print("Bosque County Parcel Map Viewer")
    print("=" * 70)
    print()

    geojson_file = get_latest_geojson()

    if geojson_file:
        print(f"✓ Found parcel data: {geojson_file.name}")
        print()
    else:
        print("⚠ No parcel data found")
        print("  Run 'python test_scraper.py' or 'python scraper.py' first")
        print("  Demo mode will be shown")
        print()

    print("Starting web server...")
    print("Open in browser: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)

    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
