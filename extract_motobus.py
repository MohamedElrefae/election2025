#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_voter_extractor import VoterPDFExtractor
import logging

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    pdf_path = "motobus .pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found: {pdf_path}")
        return 1
    
    try:
        logger.info("Starting extraction of motobus.pdf...")
        
        extractor = VoterPDFExtractor()
        locations, voters = extractor.process_pdf(pdf_path)
        
        if not locations:
            logger.error("No location data extracted.")
            return 1
        
        output_dir = "output"
        extractor.export_to_csv(output_dir)
        extractor.export_to_json(output_dir)
        extractor.export_to_sql(output_dir)
        extractor.generate_summary_report(output_dir)
        
        logger.info(f"Extraction completed! Found {len(locations)} locations and {len(voters)} voters")
        return 0
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
