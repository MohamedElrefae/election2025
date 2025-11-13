import PyPDF2
import pandas as pd
import re
import json
import sys

def extract_text_from_pdf(pdf_path):
    """Extract text from all pages of the PDF"""
    print(f"Extracting text from {pdf_path}...")
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        
        full_text = ""
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            full_text += f"\n\n--- PAGE {page_num+1} ---\n"
            full_text += text
            print(f"Text extracted from page {page_num+1}/{num_pages}")
    
    return full_text, num_pages

def parse_location_data(text, page_num):
    """Parse location information from the header of each page"""
    location_data = {
        'page': page_num,
        'location_number': '',
        'location_name': '',
        'location_address': '',
        'governorate': '',
        'district': '',
        'main_committee_id': '',
        'police_department': '',
        'total_voters': 0
    }
    
    # This is a placeholder. The actual parsing logic will depend on how the PDF is structured.
    # We need to examine the extracted text to determine the exact patterns.
    
    return location_data

def parse_voter_data(text, location_id, page_num):
    """Parse individual voter data from the page text"""
    voters = []
    
    # This is a placeholder. The actual parsing logic will depend on how the PDF is structured.
    # We need to examine the extracted text to determine the exact patterns.
    
    return voters

def show_pdf_sample(pdf_path, num_pages=3):
    """Show sample text from the first few pages to understand structure"""
    print(f"Extracting sample text from {pdf_path}...")
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        for page_num in range(min(num_pages, len(pdf_reader.pages))):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            print(f"\n\n--- PAGE {page_num+1} SAMPLE ---")
            print(text[:2000])  # Show first 2000 characters

if __name__ == "__main__":
    pdf_path = "motobus .pdf"
    
    # First, let's look at a sample of the PDF to understand its structure
    show_pdf_sample(pdf_path, 3)
    
    # Extract all text from the PDF
    full_text, num_pages = extract_text_from_pdf(pdf_path)
    
    # Save the raw extracted text for reference
    with open("extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    
    print(f"Full text extracted and saved to extracted_text.txt")
    print(f"PDF has {num_pages} pages")
    
    # After examining the text, we would implement the parsing functions
    # For now, let's create empty templates for the output files
    locations_df = pd.DataFrame(columns=[
        'location_id', 'location_number', 'location_name', 'location_address',
        'governorate', 'district', 'main_committee_id', 'police_department', 'total_voters'
    ])
    
    voters_df = pd.DataFrame(columns=[
        'voter_id', 'full_name', 'location_id', 'source_page'
    ])
    
    # Save empty templates
    locations_df.to_csv("locations.csv", index=False, encoding="utf-8")
    voters_df.to_csv("voters.csv", index=False, encoding="utf-8")
    
    print("Template CSV files created: locations.csv and voters.csv")
    print("Next step: Examine extracted_text.txt to understand the PDF structure and update the parsing functions.")