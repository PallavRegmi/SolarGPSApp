
# Solar GPS App

A Flask web app to upload solar-array JPEGs, extract GPS EXIF data (lat, lon, alt), classify defects, and export CSV/KML.

**Live Demo:** https://7quadsquad7.pythonanywhere.com  
**Code:** https://github.com/PallavRegmi/SolarGPSApp



## Features

- Two-step upload with duplicate check  
- EXIF GPS → decimal conversion  
- 25-category defect dropdown per image  
- CSV export: Filename | Latitude (Decimal) | Longitude (Decimal) | Altitude | Classification  
- KML export: styled placemarks for Google Earth  
- Responsive Bootstrap 5 UI  
- JPEG-only (≤500 MB), error handling  



## Tech Stack

Python • Flask • exif • Pandas • Bootstrap 5 • HTML/CSS/JS • KML/XML • PythonAnywhere



## Quick Start

1. **Clone & install**  

   git clone https://github.com/PallavRegmi/SolarGPSApp.git
   cd SolarGPSApp
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   mkdir temp_exports


2. **Run**


   export FLASK_APP=app.py
   flask run

3. **Use**
   – Start first upload → optional second batch → classify → download CSV/KML



## Structure

```
SolarGPSApp/
├─ app.py
├─ requirements.txt
├─ templates/
│  ├─ index.html
│  ├─ upload_step1.html
│  ├─ after_first_upload.html
│  ├─ upload_step2.html
│  └─ results.html
├─ static/images/ESS.png, SRTL.png
└─ temp_exports/
   ├─ accumulated_results.json
   ├─ results.csv
   └─ results.kml

