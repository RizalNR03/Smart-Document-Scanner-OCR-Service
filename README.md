# Smart Document Scanner OCR

Aplikasi berbasis **Python**, **OpenCV**, dan **Flask** untuk melakukan pemindaian dokumen kartu nama secara cerdas. Sistem ini mampu mendeteksi area dokumen, melakukan koreksi perspektif (*automatic crop*), meningkatkan kualitas gambar, mengekstraksi teks menggunakan OCR, serta menghasilkan metadata dalam format JSON. Aplikasi juga mendukung pemrosesan banyak gambar (*batch processing*).

---

## Features

- Document Detection menggunakan OpenCV
- Automatic Perspective Correction (Dewarp)
- Image Enhancement untuk meningkatkan akurasi OCR
- OCR Extraction menggunakan EasyOCR
- Structured JSON Output
- Batch Processing
- Flask Web Interface
- Docker Support

---

## Tech Stack

- Python 3.x
- OpenCV
- EasyOCR
- Flask
- NumPy
- Docker

---

## Project Structure

```text
smart-document-scanner/
│
├── app/
│   ├── pipeline.py
│   └── templates/
│       ├── index.html
│       └── batch_results.html
│
├── dataset/
│
├── outputs/
│   ├── debug/
│   ├── processed/
│   └── json/
│
├── main.py
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# Processing Pipeline

The application processes every image using the following pipeline:

```text
Input Image
      │
      ▼
Document Detection
      │
      ▼
Perspective Correction
      │
      ▼
Image Enhancement
      │
      ▼
OCR Extraction
      │
      ▼
Structured Field Parsing
      │
      ▼
Metadata JSON Output
```

---

# Image Processing Pipeline

The document detection stage consists of:

```text
Input Image
      │
      ▼
Resize
      │
      ▼
Grayscale
      │
      ▼
Gaussian Blur
      │
      ▼
Canny Edge Detection
      │
      ▼
Contour Detection
      │
      ▼
Perspective Transform
      │
      ▼
Enhanced Document
      │
      ▼
OCR
```

---

# Installation

## Method 1 — Local Installation (Recommended for Development)

### 1. Clone Repository

```bash
git clone <repository-url>
cd smart-document-scanner
```

### 2. Create Virtual Environment

Windows

```bash
python -m venv .venv
```

Linux / macOS

```bash
python3 -m venv .venv
```

---

### 3. Activate Virtual Environment

Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

Windows CMD

```cmd
.venv\Scripts\activate.bat
```

Linux / macOS

```bash
source .venv/bin/activate
```

---

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 5. Run Application

```bash
python main.py
```

Open browser:

```
http://localhost:8080
```

---

# Method 2 — Docker

## Build Image

```bash
docker build -t smart-document-scanner .
```

## Run Container

```bash
docker run -p 8080:8080 smart-document-scanner
```

Open browser:

```
http://localhost:8080
```

---

## Stop Container

```bash
docker stop smart-document-scanner
```

---

## Remove Container

```bash
docker rm smart-document-scanner
```

---

## Remove Image

```bash
docker rmi smart-document-scanner
```

---

# Batch Processing

Place all sample business card images inside:

```text
dataset/
```

Example:

```text
dataset/
├── card_01.jpg
├── card_02.jpg
├── card_03.jpg
├── card_04.jpg
├── card_05.jpg
```

Run batch processing from browser:

```
http://localhost:8080/batch
```

The application will:

- Detect the document
- Correct perspective
- Enhance image quality
- Perform OCR
- Extract structured information
- Save metadata JSON
- Generate visualization results

---

# Output Directory

```text
outputs/

├── debug/
│   ├── detected_contour.jpg
│   ├── edges.jpg
│   └── threshold.jpg
│
├── processed/
│   ├── corrected_document.jpg
│   ├── enhanced_document.jpg
│   └── ocr_result.jpg
│
└── json/
    ├── result_01.json
    ├── result_02.json
    └── ...
```

---

# JSON Output Example

```json
{
  "document_detected": true,
  "rotation_angle": -7.4,
  "processing_time_ms": 143,
  "ocr_confidence": 0.93,
  "image_width": 1280,
  "image_height": 720,
  "fields": {
    "name": "Alexander William",
    "company": "Nexora Solutions",
    "email": "alex.william@nexorasolutions.com",
    "phone": "+62 812-3456-7890",
  }
}
```

---

# Testing Scenarios

| Scenario | Expected Result |
|-----------|-----------------|
| Rotated Business Card | Perspective corrected |
| Low Light | OCR remains readable |
| Shadow | Document still detected |
| Multiple Objects | Largest document selected |
| No Document | Graceful failure |
| Noisy Background | Stable detection |
| Partial Blur | OCR partially preserved |

---

# Assumptions

- One primary business card per image.
- Business card occupies a significant portion of the image.
- Images are stored in JPG or PNG format.
- OCR language is English.

---

# Limitations

- Multiple overlapping documents are not supported.
- Heavy reflections may reduce OCR accuracy.
- Extremely blurred images may fail during document detection.
- OCR accuracy depends on image quality.

---

# Future Improvements

- PaddleOCR integration
- Faster contour detection using C++
- GPU acceleration
- REST API
- Automatic document classification
- Multi-document detection

---

# Author
Rizal Naufal Robbani

Python • OpenCV • OCR • Docker
