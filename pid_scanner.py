import json
import re
import cv2
import numpy as np
import pandas as pd
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import pdfplumber
from typing import Dict, List, Tuple, Any
import os

# Configure Tesseract path for Windows
if os.name == 'nt':  # Windows
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\AppData\Local\Tesseract-OCR\tesseract.exe'
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break
    
    # Configure Poppler path for Windows
    poppler_path = r'C:\poppler\Library\bin'
    if os.path.exists(poppler_path):
        # Add poppler to PATH for this session
        current_path = os.environ.get('PATH', '')
        if poppler_path not in current_path:
            os.environ['PATH'] = poppler_path + os.pathsep + current_path


class PIDScanner:
    def __init__(self, config_path: str = "config.json"):
        """Initialize the P&ID scanner with configuration settings."""
        self.config = self.load_config(config_path)
        self.extracted_data = {}
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results."""
        if self.config['ocr_settings']['preprocessing']['denoise']:
            image = cv2.medianBlur(image, 3)
        
        if self.config['ocr_settings']['preprocessing']['enhance_contrast']:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            cl = clahe.apply(l_channel)
            image = cv2.merge((cl, a, b))
            image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)
        
        if self.config['ocr_settings']['preprocessing']['sharpen']:
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            image = cv2.filter2D(image, -1, kernel)
        
        return image
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract text from PDF using multiple methods."""
        text_content = []
        
        # Method 1: Using pdfplumber for text extraction
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                        print(f"Extracted {len(text)} characters from page via pdfplumber")
        except Exception as e:
            print(f"Error extracting text with pdfplumber: {e}")
        
        # If we got meaningful text from pdfplumber, return it
        if text_content:
            combined_text = " ".join(text_content)
            # Check if the text is actually useful (more than just whitespace)
            if len(combined_text.strip()) > 50:  # At least 50 characters of real text
                print(f"Successfully extracted meaningful text from {len(text_content)} pages using pdfplumber")
                return text_content
            else:
                print(f"pdfplumber extracted only {len(combined_text.strip())} characters - trying OCR instead")
                text_content = []  # Clear it so we fall through to OCR
        
        # Method 2: Convert PDF to images and use OCR (requires Poppler)
        try:
            print("Attempting OCR extraction (requires Poppler)...")
            images = convert_from_path(pdf_path, dpi=self.config['ocr_settings']['dpi'])
            for i, image in enumerate(images):
                print(f"Processing page {i+1} with OCR...")
                # Convert PIL image to numpy array
                img_array = np.array(image)
                
                # Preprocess image
                if len(img_array.shape) == 3:
                    img_array = self.preprocess_image(img_array)
                
                # Perform OCR
                ocr_config = self.config['ocr_settings']['tesseract_config']
                text = pytesseract.image_to_string(img_array, config=ocr_config)
                if text.strip():
                    text_content.append(text)
                    print(f"OCR extracted {len(text)} characters from page {i+1}")
                
        except Exception as e:
            print(f"Error with OCR extraction: {e}")
            print("Note: OCR requires Poppler to be installed. Install from: https://poppler.freedesktop.org/")
        
        return text_content
    
    def extract_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """Extract data matching specific patterns from text."""
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            matches.extend(found)
        return list(set(matches))  # Remove duplicates
    
    def scan_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Main method to scan PDF and extract P&ID data."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Extract all text from PDF
        text_content = self.extract_text_from_pdf(pdf_path)
        combined_text = " ".join(text_content)
        
        # Extract data based on configuration
        extraction_settings = self.config['extraction_settings']
        results = {}
        
        for category, settings in extraction_settings.items():
            if settings.get('enabled', True):
                patterns = settings.get('patterns', [])
                matches = self.extract_patterns(combined_text, patterns)
                results[category] = {
                    'count': len(matches),
                    'items': matches
                }
        
        # Store results
        self.extracted_data = {
            'pdf_path': pdf_path,
            'extraction_results': results,
            'total_pages': len(text_content),
            'raw_text_preview': combined_text[:500] + "..." if len(combined_text) > 500 else combined_text
        }
        
        return self.extracted_data
    
    def get_summary(self) -> Dict[str, int]:
        """Get a summary of extracted data counts."""
        if not self.extracted_data:
            return {}
        
        summary = {}
        for category, data in self.extracted_data['extraction_results'].items():
            summary[category] = data['count']
        
        return summary
    
    def export_to_csv(self, output_path: str) -> None:
        """Export extracted data to CSV format."""
        if not self.extracted_data:
            raise ValueError("No data to export. Run scan_pdf() first.")
        
        # Prepare data for CSV
        rows = []
        for category, data in self.extracted_data['extraction_results'].items():
            for item in data['items']:
                rows.append({
                    'category': category,
                    'item': item,
                    'pdf_source': self.extracted_data['pdf_path']
                })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
        print(f"Data exported to {output_path}")
    
    def export_to_json(self, output_path: str) -> None:
        """Export extracted data to JSON format."""
        if not self.extracted_data:
            raise ValueError("No data to export. Run scan_pdf() first.")
        
        with open(output_path, 'w') as f:
            json.dump(self.extracted_data, f, indent=2)
        print(f"Data exported to {output_path}")
    
    def filter_results(self, category: str = None, min_count: int = 1) -> Dict[str, Any]:
        """Filter results based on category and minimum count."""
        if not self.extracted_data:
            return {}
        
        filtered = {}
        for cat, data in self.extracted_data['extraction_results'].items():
            if category and cat != category:
                continue
            if data['count'] >= min_count:
                filtered[cat] = data
        
        return filtered
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update configuration settings."""
        self.config.update(new_config)
    
    def add_custom_pattern(self, category: str, pattern: str) -> None:
        """Add a custom extraction pattern."""
        if category not in self.config['extraction_settings']:
            self.config['extraction_settings'][category] = {
                'enabled': True,
                'patterns': []
            }
        
        self.config['extraction_settings'][category]['patterns'].append(pattern)


if __name__ == "__main__":
    # Example usage
    scanner = PIDScanner()
    
    # Example of scanning a PDF file
    # pdf_path = "sample_pid.pdf"
    # results = scanner.scan_pdf(pdf_path)
    # print(json.dumps(results, indent=2))
    
    # Example of exporting results
    # scanner.export_to_csv("extracted_data.csv")
    # scanner.export_to_json("extracted_data.json")
    
    print("P&ID Scanner initialized. Use scan_pdf() method to process a PDF file.")