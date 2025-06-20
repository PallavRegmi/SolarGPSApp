from flask import Flask, request, render_template, send_file, redirect, url_for
from exif import Image
import os
import pandas as pd
import base64
import json

app = Flask(__name__)

# Allow up to 500 MB per request
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500 MB

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_EXPORTS_DIR = os.path.join(BASE_DIR, 'temp_exports')
os.makedirs(TEMP_EXPORTS_DIR, exist_ok=True)

# File to persist accumulated results across requests
ACCUMULATED_RESULTS_FILE = os.path.join(TEMP_EXPORTS_DIR, 'accumulated_results.json')

def load_accumulated_results():
    if os.path.exists(ACCUMULATED_RESULTS_FILE):
        with open(ACCUMULATED_RESULTS_FILE, 'r') as f:
            return json.load(f)
    else:
        return []

def save_accumulated_results(results):
    with open(ACCUMULATED_RESULTS_FILE, 'w') as f:
        json.dump(results, f)

def is_duplicate(results, filename):
    for entry in results:
        if entry['filename'] == filename:
            return True
    return False

def extract_gps_data_from_bytes(file_bytes):
    """
    Extract GPS latitude, longitude, altitude (plus references) from in-memory bytes.
    Returns ((lat_dms, lat_ref), (lon_dms, lon_ref), alt) or None if missing.
    """
    exif_img = Image(file_bytes)
    if exif_img.has_exif:
        try:
            lat_dms = exif_img.gps_latitude
            lon_dms = exif_img.gps_longitude
            alt = exif_img.gps_altitude
            lat_ref = exif_img.gps_latitude_ref
            lon_ref = exif_img.gps_longitude_ref
            return (lat_dms, lat_ref), (lon_dms, lon_ref), alt
        except AttributeError:
            print("No GPS data found in this file.")
            return None
    else:
        print("No EXIF data found in this file.")
        return None

def convert_to_decimal_degrees(dms_tuple, ref):
    """
    Converts (degrees, minutes, seconds) to decimal degrees.
    If ref is 'S' or 'W', the result is negative.
    """
    degrees, minutes, seconds = dms_tuple
    decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal_degrees = -decimal_degrees
    return decimal_degrees

def export_to_csv(data, output_path):
    """
    Exports a CSV with columns:
      Filename,
      Latitude (Decimal),
      Longitude (Decimal),
      Altitude,
      Classification
    """
    # 1. Mapping from issue code to human-readable label:
    classification_map = {
        "1":  "No issue - Normal image",
        "2":  "DC Combiner - Offline",
        "3":  "Inverter - Offline",
        "4":  "String - Open circuit",
        "5":  "Module - Open Circuit",
        "6":  "Module - Bypass Diode",
        "7":  "Module - Hot Cell",
        "8":  "Module - PID",
        "9":  "Module - Short circuit",
        "10": "Module - Shading/vegetation",
        "11": "Module - Soiling",
        "12": "Other thermal issue",
        "13": "Delamination",
        "14": "Encapsulant discoloration",
        "15": "Burnt cell",
        "16": "Cell cracks",
        "17": "Snail tracks",
        "18": "Complex crack",
        "19": "Broken glass",
        "20": "Ribbon tab",
        "21": "Corrosion",
        "22": "Soiling",
        "23": "Frame damage",
        "24": "Other visual defect",
        "25": "No issue - Normal Image"
    }

    rows = []
    for entry in data:
        code = str(entry.get('issue', '1'))
        label = classification_map.get(code, "Unknown")
        rows.append({
            'Filename':             entry['filename'],
            'Latitude (Decimal)':   entry['latitude_decimal'],
            'Longitude (Decimal)':  entry['longitude_decimal'],
            'Altitude':             entry['altitude'],
            'Classification':       label
        })

    df = pd.DataFrame(rows, columns=[
        'Filename',
        'Latitude (Decimal)',
        'Longitude (Decimal)',
        'Altitude',
        'Classification'
    ])
    df.to_csv(output_path, index=False)



def export_to_kml(data, output_path):
    """
    Creates a KML file with one Placemark per image.
    Coordinates in lon,lat,alt order.
    Each placemark style is determined by its 'issue' classification.
    """
    # Mapping of issue codes to style properties
    styles = {
        "1": {"color": "ff00ff00", "icon": "http://maps.google.com/mapfiles/kml/shapes/star.png"},
        "2": {"color": "ff0000ff", "icon": "http://maps.google.com/mapfiles/kml/shapes/arrow.png"},
        "3": {"color": "ff0000aa", "icon": "http://maps.google.com/mapfiles/kml/shapes/arrow.png"},
        "4": {"color": "ff00aaff", "icon": "http://maps.google.com/mapfiles/kml/shapes/arrow.png"},
        "5": {"color": "ff00ffff", "icon": "http://maps.google.com/mapfiles/kml/shapes/arrow.png"},
        "6": {"color": "ff00ffff", "icon": "http://maps.google.com/mapfiles/kml/shapes/arrow-reverse.png"},
        "7": {"color": "ff0000aa", "icon": "http://maps.google.com/mapfiles/kml/shapes/forbidden.png"},
        "8": {"color": "ffff0000", "icon": "http://maps.google.com/mapfiles/kml/shapes/triangle.png"},
        "9": {"color": "ff00aaff", "icon": "http://maps.google.com/mapfiles/kml/shapes/arrow-reverse.png"},
        "10": {"color": "ff00ffff", "icon": "http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png"},
        "11": {"color": "ffb1b1b1", "icon": "http://maps.google.com/mapfiles/kml/pushpin/wht-pushpin.png"},
        "12": {"color": "ff00aaff", "icon": "http://maps.google.com/mapfiles/kml/shapes/donut.png"},
        "13": {"color": "ffffffff", "icon": "http://maps.google.com/mapfiles/kml/shapes/square.png"},
        "14": {"color": "ff0055aa", "icon": "http://maps.google.com/mapfiles/kml/shapes/info-i.png"},
        "15": {"color": "ff0000ff", "icon": "http://maps.google.com/mapfiles/kml/shapes/forbidden.png"},
        "16": {"color": "ffffff00", "icon": "http://maps.google.com/mapfiles/kml/shapes/square.png"},
        "17": {"color": "ffff0000", "icon": "http://maps.google.com/mapfiles/kml/shapes/square.png"},
        "18": {"color": "ff00aaff", "icon": "http://maps.google.com/mapfiles/kml/shapes/triangle.png"},
        "19": {"color": "ff00aaff", "icon": "http://maps.google.com/mapfiles/kml/shapes/forbidden.png"},
        "20": {"color": "ff0055aa", "icon": "http://maps.google.com/mapfiles/kml/paddle/wht-blank.png"},
        "21": {"color": "ff00ffff", "icon": "http://maps.google.com/mapfiles/kml/shapes/forbidden.png"},
        "22": {"color": "ffb1b1b1", "icon": "http://maps.google.com/mapfiles/kml/paddle/wht-blank.png"},
        "23": {"color": "ffffff00", "icon": "http://maps.google.com/mapfiles/kml/shapes/triangle.png"},
        "24": {"color": "ffffffff", "icon": "http://maps.google.com/mapfiles/kml/shapes/polygon.png"},
        "25": {"color": "ff00ff00", "icon": "http://maps.google.com/mapfiles/kml/paddle/wht-blank.png"}
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('  <Document>\n')

        # Write style definitions for all issue codes
        for key, style in styles.items():
            f.write(f'    <Style id="issue{key}">\n')
            f.write('      <IconStyle>\n')
            f.write(f'        <color>{style["color"]}</color>\n')
            f.write('        <Icon>\n')
            f.write(f'          <href>{style["icon"]}</href>\n')
            f.write('        </Icon>\n')
            f.write('      </IconStyle>\n')
            f.write('    </Style>\n')

        # Write one Placemark for each image entry in data
        for entry in data:
            issue = str(entry.get('issue', '1'))
            filename = entry['filename']
            lat = entry['latitude_decimal']
            lon = entry['longitude_decimal']
            alt = entry['altitude']

            f.write('    <Placemark>\n')
            f.write(f'      <name>{filename}</name>\n')
            f.write('      <description>Thermal Image.</description>\n')
            f.write(f'      <styleUrl>#issue{issue}</styleUrl>\n')
            f.write('      <Point>\n')
            f.write(f'        <coordinates>{lon},{lat},{alt}</coordinates>\n')
            f.write('      </Point>\n')
            f.write('    </Placemark>\n')
        f.write('  </Document>\n')
        f.write('</kml>\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_step1', methods=['GET', 'POST'])
def upload_step1():
    if request.method == 'POST':
        # Start fresh for a new session
        accumulated_results = []
        if 'images' not in request.files:
            return "No files uploaded."
        files = request.files.getlist('images')
        for file in files:
            if not file.filename.lower().endswith(('.jpg', '.jpeg')):
                return "The result can not be processed. User uploaded one or more file that is not a JPEG file"
            file_bytes = file.read()
            gps_data = extract_gps_data_from_bytes(file_bytes)
            if gps_data:
                (lat_dms, lat_ref), (lon_dms, lon_ref), alt = gps_data
                lat_decimal = convert_to_decimal_degrees(lat_dms, lat_ref)
                lon_decimal = convert_to_decimal_degrees(lon_dms, lon_ref)
                lat_original = f"{lat_dms[0]}° {lat_dms[1]}' {lat_dms[2]}\" {lat_ref}"
                lon_original = f"{lon_dms[0]}° {lon_dms[1]}' {lon_dms[2]}\" {lon_ref}"
            else:
                lat_decimal = lon_decimal = alt = 0
                lat_original = lon_original = "N/A"
            image_b64 = base64.b64encode(file_bytes).decode('utf-8')
            if not is_duplicate(accumulated_results, file.filename):
                accumulated_results.append({
                    'filename': file.filename,
                    'latitude_original': lat_original,
                    'latitude_decimal': lat_decimal,
                    'longitude_original': lon_original,
                    'longitude_decimal': lon_decimal,
                    'altitude': alt,
                    'image_data': image_b64
                })
        save_accumulated_results(accumulated_results)
        return render_template('after_first_upload.html')
    return render_template('upload_step1.html')

@app.route('/upload_step2', methods=['GET', 'POST'])
def upload_step2():
    if request.method == 'POST':
        accumulated_results = load_accumulated_results()
        if 'images' not in request.files:
            return "No files uploaded."
        files = request.files.getlist('images')
        for file in files:
            if not file.filename.lower().endswith(('.jpg', '.jpeg')):
                return ("The result can not be processed.\nEither: User uploaded one or more file that is not a JPEG file.\n"
                        "Or: The user has not uploaded any files.")
            file_bytes = file.read()
            gps_data = extract_gps_data_from_bytes(file_bytes)
            if gps_data:
                (lat_dms, lat_ref), (lon_dms, lon_ref), alt = gps_data
                lat_decimal = convert_to_decimal_degrees(lat_dms, lat_ref)
                lon_decimal = convert_to_decimal_degrees(lon_dms, lon_ref)
                lat_original = f"{lat_dms[0]}° {lat_dms[1]}' {lat_dms[2]}\" {lat_ref}"
                lon_original = f"{lon_dms[0]}° {lon_dms[1]}' {lon_dms[2]}\" {lon_ref}"
            else:
                lat_decimal = lon_decimal = alt = 0
                lat_original = lon_original = "N/A"
            image_b64 = base64.b64encode(file_bytes).decode('utf-8')
            if not is_duplicate(accumulated_results, file.filename):
                accumulated_results.append({
                    'filename': file.filename,
                    'latitude_original': lat_original,
                    'latitude_decimal': lat_decimal,
                    'longitude_original': lon_original,
                    'longitude_decimal': lon_decimal,
                    'altitude': alt,
                    'image_data': image_b64
                })
        save_accumulated_results(accumulated_results)
        return redirect(url_for('final_results'))
    return render_template('upload_step2.html')

@app.route('/skip_second_upload')
def skip_second_upload():
    return redirect(url_for('final_results'))

@app.route('/final_results')
def final_results():
    accumulated_results = load_accumulated_results()
    csv_path = os.path.join(TEMP_EXPORTS_DIR, 'results.csv')
    kml_path = os.path.join(TEMP_EXPORTS_DIR, 'results.kml')
    export_to_csv(accumulated_results, csv_path)
    export_to_kml(accumulated_results, kml_path)
    return render_template('results.html', results=accumulated_results)

# New route to update classification selections and regenerate KML/CSV
@app.route('/update_classification', methods=['POST'])
def update_classification():
    accumulated_results = load_accumulated_results()
    for idx, result in enumerate(accumulated_results):
        issue_value = request.form.get(f'issue_{idx}', "1")
        result['issue'] = issue_value
    save_accumulated_results(accumulated_results)
    csv_path = os.path.join(TEMP_EXPORTS_DIR, 'results.csv')
    kml_path = os.path.join(TEMP_EXPORTS_DIR, 'results.kml')
    export_to_csv(accumulated_results, csv_path)
    export_to_kml(accumulated_results, kml_path)
    return redirect(url_for('final_results'))

@app.route('/download_csv')
def download_csv():
    csv_path = os.path.join(TEMP_EXPORTS_DIR, 'results.csv')
    if not os.path.exists(csv_path):
        return "CSV file not found. Please upload images first."
    return send_file(
        csv_path,
        as_attachment=True,
        mimetype='text/csv',
        download_name='results.csv'
    )

@app.route('/download_kml')
def download_kml():
    kml_path = os.path.join(TEMP_EXPORTS_DIR, 'results.kml')
    if not os.path.exists(kml_path):
        return "KML file not found. Please upload images first."
    return send_file(
        kml_path,
        as_attachment=True,
        mimetype='application/vnd.google-earth.kml+xml',
        download_name='results.kml'
    )

if __name__ == '__main__':
    app.run(debug=True)
