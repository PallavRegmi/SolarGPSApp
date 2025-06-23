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

## Prerequisites

- Python 3.8+  
- `pip` (Python package manager)  
- (Optional) [PythonAnywhere](https://www.pythonanywhere.com/) account for deployment  

---

## 🚀 Installation

1. **Clone the repository**  

   git clone https://github.com/your-username/solar-gps-app.git
   cd solar-gps-app


2. **Create & activate a virtual environment**

   ```
   python3 -m venv venv
   source venv/bin/activate     # Linux / macOS
   venv\Scripts\activate        # Windows
   ```

3. **Install dependencies**


   pip install -r requirements.txt


4. **Create required directories**


   mkdir temp_exports


---

##  Configuration

* **Max upload size:**
  Controlled by `app.config['MAX_CONTENT_LENGTH']` in `app.py` (default: 500 MB).

* **Static assets:**
  Place your logo images under `static/images/` (e.g. `static/images/ESS.png`, `static/images/SRTL.png`).

---

##  Running Locally

```
export FLASK_APP=app.py        # Linux / macOS
set FLASK_APP=app.py           # Windows
flask run --debug
```

Then open your browser at `http://127.0.0.1:5000/`.

---

##  Usage

1. **Landing Page**
   Click **Start First Upload**.

2. **Upload Step 1**
   Select one or more JPEG images (≤100 MB total) and click **Upload**.

3. **Second Batch (Optional)**

   * Click **Upload Second Batch** to add more images.
   * Or click **Skip Second Upload** to proceed.

4. **View & Classify Results**

   * Review the table of image previews and GPS data.
   * Use the **Issue** dropdown next to each image to select a defect classification.
   * Click **Save Classifications** (at the bottom of the table) to apply and regenerate exports.

5. **Download Exports**

   * **Download CSV**: Get a CSV with human-readable classifications.
   * **Download KML**: Get a KML file with styled placemarks for use in Google Earth.

---

## 📁 Project Structure

```
.
├── app.py
├── requirements.txt
├── templates/
│   ├── index.html
│   ├── upload_step1.html
│   ├── after_first_upload.html
│   ├── upload_step2.html
│   └── results.html
├── static/
│   └── images/
│       ├── ESS.png
│       └── SRTL.png
└── temp_exports/
    ├── accumulated_results.json
    ├── results.csv
    └── results.kml
```

---

## 🤝 Contributing

1. Fork this repository.
2. Create a feature branch: `git checkout -b feature/YourFeature`.
3. Commit your changes: `git commit -m "Add your feature"`.
4. Push to the branch: `git push origin feature/YourFeature`.
5. Open a Pull Request.

---
