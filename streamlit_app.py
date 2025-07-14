import streamlit as st
import json
import pandas as pd
from pid_scanner import PIDScanner
import os
import tempfile


def main():
    st.set_page_config(
        page_title="P&ID Scanner - Digital Energy Services", 
        page_icon="📄", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header with branding
    st.title("P&ID Scanner")
    st.markdown("**Professional P&ID Analysis Tool by Digital Energy Services**")
    st.markdown("Upload a PDF P&ID drawing and extract equipment data using advanced OCR and pattern matching")
    
    # Add info about the service
    with st.expander("ℹ️ About This Tool"):
        st.markdown("""
        This P&ID Scanner extracts key data from Process and Instrumentation Diagrams including:
        - Equipment tags and identifiers
        - Valve specifications and locations  
        - Instrument tags and types
        - Pipe specifications and sizing
        - Pressure ratings and material specs
        
        **Powered by Digital Energy Services** - Professional engineering analysis tools.
        Visit [digitalenergyservices.ca](https://www.digitalenergyservices.ca) for more services.
        """)
    
    # Initialize scanner
    if 'scanner' not in st.session_state:
        st.session_state.scanner = PIDScanner()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Load current config
        config = st.session_state.scanner.config
        
        st.subheader("Data Extraction Settings")
        
        # Equipment Tags
        equipment_enabled = st.checkbox("Equipment Tags", 
                                       value=config['extraction_settings']['equipment_tags']['enabled'])
        if equipment_enabled:
            equipment_patterns = st.text_area("Equipment Tag Patterns (one per line)", 
                                            value="\n".join(config['extraction_settings']['equipment_tags']['patterns']))
        
        # Valves
        valves_enabled = st.checkbox("Valves", 
                                   value=config['extraction_settings']['valves']['enabled'])
        if valves_enabled:
            valve_patterns = st.text_area("Valve Patterns (one per line)", 
                                        value="\n".join(config['extraction_settings']['valves']['patterns']))
        
        # Instruments
        instruments_enabled = st.checkbox("Instruments", 
                                        value=config['extraction_settings']['instruments']['enabled'])
        if instruments_enabled:
            instrument_patterns = st.text_area("Instrument Patterns (one per line)", 
                                             value="\n".join(config['extraction_settings']['instruments']['patterns']))
        
        # Pipe Specifications
        pipes_enabled = st.checkbox("Pipe Specifications", 
                                  value=config['extraction_settings']['pipe_specifications']['enabled'])
        if pipes_enabled:
            pipe_patterns = st.text_area("Pipe Spec Patterns (one per line)", 
                                       value="\n".join(config['extraction_settings']['pipe_specifications']['patterns']))
        
        # Pressure Ratings
        pressure_enabled = st.checkbox("Pressure Ratings", 
                                     value=config['extraction_settings']['pressure_ratings']['enabled'])
        if pressure_enabled:
            pressure_patterns = st.text_area("Pressure Rating Patterns (one per line)", 
                                           value="\n".join(config['extraction_settings']['pressure_ratings']['patterns']))
        
        # Material Specifications
        materials_enabled = st.checkbox("Material Specifications", 
                                      value=config['extraction_settings']['material_specifications']['enabled'])
        if materials_enabled:
            material_patterns = st.text_area("Material Spec Patterns (one per line)", 
                                           value="\n".join(config['extraction_settings']['material_specifications']['patterns']))
        
        # OCR Settings
        st.subheader("OCR Settings")
        dpi = st.slider("DPI", 150, 600, config['ocr_settings']['dpi'])
        denoise = st.checkbox("Denoise", value=config['ocr_settings']['preprocessing']['denoise'])
        enhance_contrast = st.checkbox("Enhance Contrast", value=config['ocr_settings']['preprocessing']['enhance_contrast'])
        sharpen = st.checkbox("Sharpen", value=config['ocr_settings']['preprocessing']['sharpen'])
        
        # Update configuration
        if st.button("Update Configuration"):
            new_config = {
                'extraction_settings': {
                    'equipment_tags': {
                        'enabled': equipment_enabled,
                        'patterns': equipment_patterns.split('\n') if equipment_enabled else []
                    },
                    'valves': {
                        'enabled': valves_enabled,
                        'patterns': valve_patterns.split('\n') if valves_enabled else []
                    },
                    'instruments': {
                        'enabled': instruments_enabled,
                        'patterns': instrument_patterns.split('\n') if instruments_enabled else []
                    },
                    'pipe_specifications': {
                        'enabled': pipes_enabled,
                        'patterns': pipe_patterns.split('\n') if pipes_enabled else []
                    },
                    'pressure_ratings': {
                        'enabled': pressure_enabled,
                        'patterns': pressure_patterns.split('\n') if pressure_enabled else []
                    },
                    'material_specifications': {
                        'enabled': materials_enabled,
                        'patterns': material_patterns.split('\n') if materials_enabled else []
                    }
                },
                'ocr_settings': {
                    'dpi': dpi,
                    'preprocessing': {
                        'denoise': denoise,
                        'enhance_contrast': enhance_contrast,
                        'sharpen': sharpen
                    },
                    'tesseract_config': config['ocr_settings']['tesseract_config']
                },
                'output_format': config['output_format']
            }
            st.session_state.scanner.update_config(new_config)
            st.success("Configuration updated!")
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("Upload PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            st.success(f"File uploaded: {uploaded_file.name}")
            
            if st.button("Scan PDF", type="primary"):
                with st.spinner("Scanning PDF... This may take a few moments."):
                    try:
                        results = st.session_state.scanner.scan_pdf(tmp_file_path)
                        st.session_state.results = results
                        st.success("PDF scanned successfully!")
                    except Exception as e:
                        st.error(f"Error scanning PDF: {str(e)}")
                    finally:
                        # Clean up temporary file
                        os.unlink(tmp_file_path)
    
    with col2:
        st.header("Results")
        
        if 'results' in st.session_state:
            results = st.session_state.results
            
            # Display summary
            st.subheader("Summary")
            summary = st.session_state.scanner.get_summary()
            
            summary_df = pd.DataFrame(list(summary.items()), columns=['Category', 'Count'])
            st.dataframe(summary_df, use_container_width=True)
            
            # Display detailed results
            st.subheader("Detailed Results")
            
            for category, data in results['extraction_results'].items():
                if data['count'] > 0:
                    with st.expander(f"{category.replace('_', ' ').title()} ({data['count']} items)"):
                        for item in data['items']:
                            st.write(f"• {item}")
            
            # Export options
            st.subheader("Export Results")
            col3, col4 = st.columns(2)
            
            with col3:
                if st.button("Export to CSV"):
                    csv_path = "extracted_data.csv"
                    st.session_state.scanner.export_to_csv(csv_path)
                    
                    # Read the CSV file for download
                    with open(csv_path, 'r') as f:
                        csv_data = f.read()
                    
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name="pid_extracted_data.csv",
                        mime="text/csv"
                    )
            
            with col4:
                if st.button("Export to JSON"):
                    json_path = "extracted_data.json"
                    st.session_state.scanner.export_to_json(json_path)
                    
                    # Read the JSON file for download
                    with open(json_path, 'r') as f:
                        json_data = f.read()
                    
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name="pid_extracted_data.json",
                        mime="application/json"
                    )
            
            # Raw text preview
            with st.expander("Raw Text Preview"):
                st.text_area("Extracted Text", 
                           value=results.get('raw_text_preview', ''),
                           height=200,
                           disabled=True)
        
        else:
            st.info("Upload a PDF file and click 'Scan PDF' to see results here.")
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center'>
        <p><strong>P&ID Scanner</strong> - Professional P&ID Analysis Tool</p>
        <p>Powered by <a href='https://www.digitalenergyservices.ca' target='_blank'>Digital Energy Services</a></p>
        <p><small>© 2025 Digital Energy Services. All rights reserved.</small></p>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()