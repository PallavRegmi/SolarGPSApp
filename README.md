# Solar GPS Web App

A Flask-based web application for uploading solar‐array images, extracting GPS EXIF metadata (latitude, longitude, altitude), classifying defects, and exporting the results in CSV and KML formats.

---

##  Features

- **Two-Step Image Upload**  
  Accumulate batches of JPEG images without duplication and extract EXIF GPS data.

- **EXIF Parsing & Geo-Conversion**  
  Reads DMS (degrees/minutes/seconds) GPS data using the `exif` library and converts to decimal degrees.

- **Defect Classification**  
  Per-image dropdown menu to select from 25 thermal and visual defect categories.

- **CSV Export**  
  Outputs a CSV with columns:  
  `Filename`, `Latitude (Decimal)`, `Longitude (Decimal)`, `Altitude`, **Classification**.

- **KML Export**  
  Generates a standards-compliant KML file with styled `<Placemark>` entries and custom icons/colors per defect category, viewable in Google Earth.

- **Responsive UI**  
  Built with Bootstrap 5: large navigation buttons, in-page image previews, and classification controls.

- **Deployment & Storage Management**  
  - Limits uploads to JPEG only (up to 500 MB per request).  
  - Cleans up unused files on PythonAnywhere to prevent disk-full errors.

---

## ⚙️ Prerequisites

- Python 3.8+  
- `pip` (Python package manager)  

---
