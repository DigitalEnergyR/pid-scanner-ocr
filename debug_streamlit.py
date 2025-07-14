import streamlit as st
import tempfile
import os
import subprocess
import sys

def test_ocr_dependencies():
    """Test if OCR dependencies are working"""
    results = {}
    
    # Test 1: Check if tesseract is installed
    try:
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        results['tesseract'] = f"✅ Tesseract found: {result.stdout.split()[1]}"
    except Exception as e:
        results['tesseract'] = f"❌ Tesseract not found: {str(e)}"
    
    # Test 2: Check if poppler is installed
    try:
        result = subprocess.run(['pdftoppm', '-h'], capture_output=True, text=True)
        results['poppler'] = "✅ Poppler (pdftoppm) found"
    except Exception as e:
        results['poppler'] = f"❌ Poppler not found: {str(e)}"
    
    # Test 3: Check Python packages
    try:
        import cv2
        results['opencv'] = f"✅ OpenCV found: {cv2.__version__}"
    except Exception as e:
        results['opencv'] = f"❌ OpenCV not found: {str(e)}"
    
    try:
        import pytesseract
        results['pytesseract'] = "✅ pytesseract found"
    except Exception as e:
        results['pytesseract'] = f"❌ pytesseract not found: {str(e)}"
    
    try:
        import pdf2image
        results['pdf2image'] = "✅ pdf2image found"
    except Exception as e:
        results['pdf2image'] = f"❌ pdf2image not found: {str(e)}"
    
    return results

def test_simple_ocr():
    """Test OCR with a simple text image"""
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
        
        # Create a simple test image with text
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a white image
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add some text
        draw.text((10, 30), "P-101 TEST", fill='black')
        draw.text((10, 60), "HV-202 VALVE", fill='black')
        
        # Try OCR on this simple image
        text = pytesseract.image_to_string(img)
        return f"✅ OCR Test Result: '{text.strip()}'"
        
    except Exception as e:
        return f"❌ OCR Test Failed: {str(e)}"

def main():
    st.title("🔍 P&ID Scanner OCR Debug Tool")
    st.markdown("**Testing OCR Dependencies and Functionality**")
    
    # Test dependencies
    st.subheader("1. System Dependencies")
    deps = test_ocr_dependencies()
    for dep, status in deps.items():
        st.write(status)
    
    # Test simple OCR
    st.subheader("2. OCR Functionality Test")
    ocr_result = test_simple_ocr()
    st.write(ocr_result)
    
    # File upload test
    st.subheader("3. PDF Upload Test")
    uploaded_file = st.file_uploader("Upload a PDF to test", type=['pdf'])
    
    if uploaded_file is not None:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        st.write(f"✅ PDF uploaded successfully: {len(uploaded_file.getvalue())} bytes")
        
        # Try to convert PDF to images
        try:
            from pdf2image import convert_from_path
            st.write("📄 Converting PDF to images...")
            
            images = convert_from_path(tmp_file_path, dpi=200, first_page=1, last_page=1)
            st.write(f"✅ PDF converted to {len(images)} images")
            
            if images:
                # Display the first image
                st.image(images[0], caption="First page of PDF", width=400)
                
                # Try OCR on the first image
                try:
                    import pytesseract
                    st.write("🔍 Running OCR on first page...")
                    text = pytesseract.image_to_string(images[0])
                    
                    if text.strip():
                        st.success(f"✅ OCR extracted {len(text)} characters")
                        st.text_area("Raw OCR Output:", text, height=200)
                    else:
                        st.error("❌ OCR returned empty text")
                        
                except Exception as e:
                    st.error(f"❌ OCR failed: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ PDF conversion failed: {str(e)}")
        
        # Clean up
        os.unlink(tmp_file_path)
    
    # Environment info
    st.subheader("4. Environment Info")
    st.write(f"Python version: {sys.version}")
    st.write(f"Platform: {sys.platform}")
    st.write(f"Working directory: {os.getcwd()}")
    
    # Show environment variables
    st.subheader("5. Environment Variables")
    env_vars = ['PATH', 'TESSDATA_PREFIX', 'TESSERACT_CMD']
    for var in env_vars:
        value = os.environ.get(var, 'Not set')
        st.write(f"{var}: {value}")

if __name__ == "__main__":
    main()