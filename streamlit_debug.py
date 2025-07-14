import streamlit as st
import tempfile
import os
from pid_scanner import PIDScanner

def main():
    st.title("🔍 P&ID Scanner - Debug Mode")
    st.markdown("**Shows detailed OCR processing steps**")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload PDF for debugging", type=['pdf'])
    
    if uploaded_file is not None:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        st.success(f"📄 PDF uploaded: {len(uploaded_file.getvalue())} bytes")
        
        if st.button("Debug Scan PDF"):
            try:
                # Initialize scanner
                scanner = PIDScanner()
                
                st.write("🔄 Starting PDF processing...")
                
                # Test text extraction method directly
                st.write("📝 Testing text extraction...")
                text_content = scanner.extract_text_from_pdf(tmp_file_path)
                
                st.write(f"📊 Extracted {len(text_content)} text blocks")
                
                if text_content:
                    combined_text = " ".join(text_content)
                    st.write(f"📏 Total text length: {len(combined_text)} characters")
                    
                    # Show first 500 characters
                    preview = combined_text[:500] + "..." if len(combined_text) > 500 else combined_text
                    st.text_area("📖 Text Preview (first 500 chars):", preview, height=200)
                    
                    # Test pattern matching
                    st.write("🔍 Testing pattern matching...")
                    
                    # Test each pattern type
                    config = scanner.config['extraction_settings']
                    
                    for category, settings in config.items():
                        if settings['enabled']:
                            patterns = settings['patterns']
                            matches = scanner.extract_patterns(combined_text, patterns)
                            st.write(f"• {category}: {len(matches)} matches - {matches[:5]}...")  # Show first 5
                    
                    # Full scan
                    st.write("🚀 Running full scan...")
                    results = scanner.scan_pdf(tmp_file_path)
                    
                    st.json(results)
                    
                else:
                    st.error("❌ No text extracted from PDF")
                    
                    # Try manual OCR test
                    st.write("🔧 Attempting manual OCR test...")
                    try:
                        from pdf2image import convert_from_path
                        import pytesseract
                        
                        images = convert_from_path(tmp_file_path, dpi=200, first_page=1, last_page=1)
                        if images:
                            st.image(images[0], caption="PDF Page", width=400)
                            
                            # Direct OCR test
                            ocr_text = pytesseract.image_to_string(images[0])
                            st.write(f"📋 Direct OCR result: {len(ocr_text)} characters")
                            st.text_area("Direct OCR Text:", ocr_text, height=200)
                        
                    except Exception as e:
                        st.error(f"Manual OCR failed: {str(e)}")
                
            except Exception as e:
                st.error(f"❌ Error during processing: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
        
        # Clean up
        try:
            os.unlink(tmp_file_path)
        except:
            pass

if __name__ == "__main__":
    main()