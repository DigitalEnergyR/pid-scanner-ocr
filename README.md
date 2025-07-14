# P&ID Scanner OCR 🛢️⚡

AI-Powered P&ID Analysis Tool for Oil & Gas Engineering | Alberta Energy Tech | Piping & Instrumentation Diagram OCR

## 🚀 Features

This is the **full OCR version** that can handle scanned and flattened PDFs:

- **Full OCR capabilities** for scanned/image-based PDFs
- **Image preprocessing** (denoise, contrast, sharpen) 
- **Text extraction** from poor quality scanned documents
- **Advanced pattern matching** for equipment identification
- **Equipment tags and identifiers**
- **Valve specifications and locations**
- **Instrument tags and types**
- **Pipe specifications and sizing**
- **Pressure ratings and material specs**
- **CSV/JSON export** functionality

## 🔧 Technology Stack

- **Streamlit** - Web interface
- **Python** - Backend processing
- **Tesseract OCR** - Text extraction from images
- **OpenCV** - Image preprocessing
- **pdf2image** - PDF to image conversion
- **pdfplumber** - PDF text extraction
- **Docker** - Containerized deployment

## 📦 Deployment

### Railway
```bash
# Deploy to Railway
railway up
```

### Render
```bash
# Deploy to Render using Docker
# Uses render.yaml configuration
```

### Local Development
```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install tesseract-ocr poppler-utils

# Install Python dependencies
pip install -r requirements-production.txt

# Run the application
streamlit run streamlit_app.py
```

### Docker
```bash
# Build and run with Docker
docker build -t pid-scanner-ocr .
docker run -p 8501:8501 pid-scanner-ocr
```

## 📋 System Requirements

### Required System Packages
- `tesseract-ocr` - OCR engine
- `tesseract-ocr-eng` - English language pack
- `poppler-utils` - PDF processing utilities
- OpenCV system libraries

### Python Dependencies
See `requirements-production.txt` for complete list including:
- streamlit
- pytesseract
- opencv-python
- pdf2image
- pdfplumber
- pillow
- pandas
- numpy

## 🎯 Use Cases

Perfect for processing:
- **Scanned P&ID drawings** (where Ctrl+F doesn't work)
- **Flattened PDFs** from email/copying
- **Image-based CAD exports**
- **Poor quality field documents**
- **Legacy engineering drawings**

## 🚀 Live Demo

Deploy this repository to Railway or Render to get a working OCR-enabled P&ID scanner.

## 📊 Performance

- **Build time**: 5-10 minutes (OCR dependencies)
- **Startup time**: 30-60 seconds
- **Processing time**: 10-30 seconds per PDF page
- **Memory usage**: 200-500MB depending on PDF size

## 🆘 Support

**Powered by Digital Energy Services**

Visit [digitalenergyservices.ca](https://www.digitalenergyservices.ca) for professional engineering analysis tools and services.

## 📄 License

© 2025 Digital Energy Services. All rights reserved.

---

*This is the production OCR version designed for processing real-world engineering documents that require text extraction from images.*