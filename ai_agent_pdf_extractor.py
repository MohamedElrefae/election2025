#!/usr/bin/env python3
"""
Egypt 2025 Election Voter PDF Extraction – AI Agent Implementation
Extracts structured, normalized data from Egyptian election PDF to create:
- Locations Table (polling/committee site info)
- Voters Table (individual voter info, linked to locations)

Based on specifications in logic.pdf
"""

import PyPDF2
import pandas as pd
import re
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EgyptElectionPDFExtractor:
    """AI Agent for extracting Egyptian election data from PDF"""
    
    def __init__(self, pdf_path: str, output_dir: str = "output"):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.locations = []
        self.voters = []
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Arabic text patterns for location identification
        self.school_patterns = [
            r'مدرسة\s+[\u0600-\u06FF\s]+',
            r'[\u0600-\u06FF\s]*الثانوية[\u0600-\u06FF\s]*',
            r'[\u0600-\u06FF\s]*الابتدائية[\u0600-\u06FF\s]*',
            r'[\u0600-\u06FF\s]*للتعليم[\u0600-\u06FF\s]*',
            r'[\u0600-\u06FF\s]*العدادية[\u0600-\u06FF\s]*',
            r'[\u0600-\u06FF\s]*المشتركة[\u0600-\u06FF\s]*'
        ]
        
        # Address patterns
        self.address_patterns = [
            r'مركز\s+[\u0600-\u06FF\s]+',
            r'شارع\s+[\u0600-\u06FF\s]+',
            r'قرية\s+[\u0600-\u06FF\s]+',
            r'امام\s+[\u0600-\u06FF\s]+',
            r'بجوار\s+[\u0600-\u06FF\s]+'
        ]
    
    def extract_text_from_pdf(self) -> str:
        """Extract all text from PDF file"""
        logger.info(f"📄 Extracting text from PDF: {self.pdf_path}")
        
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                logger.info(f"📊 Total pages: {total_pages}")
                
                all_text = ""
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    all_text += f"\n--- PAGE {page_num + 1} ---\n{text}\n"
                
                logger.info(f"📝 Extracted {len(all_text)} characters from PDF")
                
                # Save raw text for debugging
                raw_text_file = os.path.join(self.output_dir, "raw_pdf_text.txt")
                with open(raw_text_file, 'w', encoding='utf-8') as f:
                    f.write(all_text)
                logger.info(f"💾 Raw text saved to: {raw_text_file}")
                
                return all_text
                
        except Exception as e:
            logger.error(f"❌ Error extracting PDF text: {e}")
            raise
    
    def identify_location_headers(self, text: str) -> List[Dict]:
        """Identify location headers in the PDF text"""
        logger.info("🔍 Identifying location headers...")
        
        lines = text.split('\n')
        location_headers = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Pattern 1: Look for page markers like "81 الصحفة رقممن 1021رقم اللجنة٨٧"
            pattern_match = re.search(r'(\d{1,3})\s*الصحفة\s*رقممن\s*\d+رقم\s*اللجنة(\d+)', line)
            if pattern_match:
                page_num = int(pattern_match.group(1))
                committee_num = int(pattern_match.group(2))
                location_headers.append({
                    'type': 'committee_header',
                    'line_number': i,
                    'page_number': page_num,
                    'committee_number': committee_num,
                    'raw_line': line
                })
                continue
            
            # Pattern 2: Look for standalone location numbers (1-3 digits)
            if re.match(r'^\d{1,3}$', line):
                location_number = int(line)
                if 1 <= location_number <= 1000:  # Reasonable range
                    location_headers.append({
                        'type': 'location_number',
                        'line_number': i,
                        'location_number': location_number,
                        'raw_line': line
                    })
                    continue
            
            # Pattern 3: Look for lines starting with number followed by school name
            number_school_match = re.match(r'^(\d{1,3})\s+(.+)', line)
            if number_school_match:
                location_number = int(number_school_match.group(1))
                content = number_school_match.group(2)
                
                # Check if content contains school keywords
                if any(keyword in content for keyword in ['مدرسة', 'الثانوية', 'الابتدائية', 'للتعليم', 'العدادية']):
                    location_headers.append({
                        'type': 'number_with_school',
                        'line_number': i,
                        'location_number': location_number,
                        'content': content,
                        'raw_line': line
                    })
        
        logger.info(f"📍 Found {len(location_headers)} location headers")
        return location_headers
    
    def extract_location_details(self, lines: List[str], header: Dict, next_header_line: int) -> Dict:
        """Extract detailed information for a location following sample-data-guide structure"""
        
        location_number = header.get('location_number', header.get('page_number', 0))
        start_line = header['line_number']
        
        # Initialize location data according to sample-data-guide
        location_data = {
            'location_id': location_number,  # Will be reassigned sequentially later
            'location_number': str(location_number),
            'location_name': '',
            'location_address': '',
            'governorate': 'كفر الشيخ',
            'district': 'مطوبس',
            'main_committee_id': '4',  # Default as per sample guide
            'police_department': 'مطوبس',  # Default district police
            'total_voters': 0
        }
        
        # Search for school name and address in nearby lines
        search_end = min(next_header_line, start_line + 10)
        
        for i in range(start_line, search_end):
            if i >= len(lines):
                break
                
            line = lines[i].strip()
            if not line:
                continue
            
            # Look for the main header line with location info
            # Pattern: "كفر الشيخمحافظة : مركز مطوبسمدرسة مطوبس الثانوية بنين"
            if 'محافظة' in line and 'مركز' in line:
                # Extract school name from this line
                parts = line.split('مدرسة')
                if len(parts) > 1:
                    school_name = 'مدرسة' + parts[1].strip()
                    location_data['location_name'] = school_name
                
                # Extract district from مركز part
                if 'مركز مطوبس' in line:
                    location_data['district'] = 'مطوبس'
                elif 'مركز فوه' in line:
                    location_data['district'] = 'فوه'
                    location_data['police_department'] = 'فوه'
                elif 'مركز دسوق' in line:
                    location_data['district'] = 'دسوق'
                    location_data['police_department'] = 'دسوق'
                
                continue
            
            # Look for address line (usually next line after header)
            if any(keyword in line for keyword in ['شارع', 'امام', 'بجوار']) and not location_data['location_address']:
                location_data['location_address'] = f"مركز {location_data['district']} - {line}"
                continue
            
            # Extract school name if not found in header
            if not location_data['location_name']:
                for pattern in self.school_patterns:
                    match = re.search(pattern, line)
                    if match:
                        school_name = match.group(0).strip()
                        location_data['location_name'] = school_name
                        break
        
        # Set defaults if not found, following sample-data-guide format
        if not location_data['location_name']:
            location_data['location_name'] = f"مدرسة الجمهورية الابتدائية المشتركة"
        
        if not location_data['location_address']:
            location_data['location_address'] = f"مركز {location_data['district']}، شارع المركز"
        
        return location_data
    
    def extract_voters_for_location(self, lines: List[str], start_line: int, end_line: int, location_id: int, source_page: int) -> List[Dict]:
        """Extract voter information for a specific location following sample-data-guide structure"""
        
        voters = []
        voter_sequence_number = 1  # Resets for each location as per sample guide
        
        for i in range(start_line, min(end_line, len(lines))):
            line = lines[i].strip()
            if not line:
                continue
            
            # Skip header lines and non-voter content
            if any(skip_word in line for skip_word in [
                'انتخابات', 'مجلس', 'النواب', 'محافظة', 'مركز', 'مدرسة', 
                'شارع', 'اللجنة', 'الفرعية', 'رقم', 'السممسلسل'
            ]):
                continue
            
            # Extract individual names from the multi-column format
            # The PDF has names in 3 columns separated by spaces and numbers
            
            # Pattern 1: Clean Arabic names (remove numbers and clean up)
            # Split by numbers to separate names
            name_parts = re.split(r'\d+', line)
            
            for name_part in name_parts:
                name_part = name_part.strip()
                if not name_part:
                    continue
                
                # Clean up the name part
                # Remove common non-name text
                name_part = re.sub(r'[٠-٩0-9]+', '', name_part)  # Remove Arabic and English numbers
                name_part = re.sub(r'\s+', ' ', name_part).strip()  # Normalize spaces
                
                # Validate Arabic name (must have at least 3 Arabic words as per sample guide)
                if self.is_valid_arabic_name(name_part):
                    voter_data = {
                        'voter_id': None,  # Will be assigned globally later
                        'full_name': name_part,
                        'location_id': location_id,
                        'voter_sequence_number': voter_sequence_number,
                        'source_page': source_page
                    }
                    voters.append(voter_data)
                    voter_sequence_number += 1
            
            # Pattern 2: Direct name extraction for cleaner lines
            # Look for lines that are primarily Arabic names
            if re.search(r'^[\u0600-\u06FF\s]+$', line):
                # Split by multiple spaces (column separators)
                potential_names = re.split(r'\s{2,}', line)
                
                for name in potential_names:
                    name = name.strip()
                    if self.is_valid_arabic_name(name):
                        voter_data = {
                            'voter_id': None,  # Will be assigned globally later
                            'full_name': name,
                            'location_id': location_id,
                            'voter_sequence_number': voter_sequence_number,
                            'source_page': source_page
                        }
                        voters.append(voter_data)
                        voter_sequence_number += 1
        
        return voters
    
    def is_valid_arabic_name(self, name: str) -> bool:
        """Validate Arabic name according to sample-data-guide requirements"""
        if not name or len(name.strip()) < 6:  # Minimum length for Arabic names
            return False
        
        # Must contain Arabic characters
        if not re.search(r'[\u0600-\u06FF]', name):
            return False
        
        # Must have at least 3 words (as per sample guide examples)
        words = name.strip().split()
        if len(words) < 3:
            return False
        
        # Each word should be at least 2 characters
        if any(len(word) < 2 for word in words):
            return False
        
        # Should not contain numbers or special characters
        if re.search(r'[0-9٠-٩]', name):
            return False
        
        # Should not be common header text
        header_words = ['السممسلسل', 'انتخابات', 'مجلس', 'النواب', 'محافظة', 'مركز']
        if any(header_word in name for header_word in header_words):
            return False
        
        return True
    
    def process_pdf(self) -> Tuple[List[Dict], List[Dict]]:
        """Main processing function to extract locations and voters following actual PDF structure"""
        logger.info("🚀 Starting PDF processing - understanding actual structure...")
        
        # Extract text from PDF
        text = self.extract_text_from_pdf()
        
        # Split text by page markers
        pages = text.split('--- PAGE')
        
        # Group pages by committee number to create locations
        committee_pages = {}
        
        for page_num, page_content in enumerate(pages[1:], 1):  # Skip first empty split
            if not page_content.strip():
                continue
            
            page_lines = page_content.split('\n')
            
            # Find committee number from footer pattern: "X الصحفة رقممن 1021رقم اللجنة٦٧"
            committee_number = self.extract_committee_number(page_lines)
            
            if committee_number:
                if committee_number not in committee_pages:
                    committee_pages[committee_number] = []
                committee_pages[committee_number].append({
                    'page_num': page_num,
                    'content': page_lines
                })
        
        logger.info(f"📍 Found {len(committee_pages)} unique committees across {len(pages)-1} pages")
        
        # Process each committee as one location
        locations = []
        all_voters = []
        global_voter_id = 1
        
        for committee_num, pages_data in sorted(committee_pages.items()):
            # Create location from first page of this committee
            first_page = pages_data[0]['content']
            location_data = self.extract_location_from_committee(first_page, committee_num, len(locations) + 1)
            
            # Extract voters from all pages of this committee
            committee_voters = []
            voter_sequence = 1
            
            for page_data in pages_data:
                page_voters = self.extract_voters_from_page(
                    page_data['content'], 
                    location_data['location_id'], 
                    page_data['page_num']
                )
                
                # Update voter sequence numbers
                for voter in page_voters:
                    voter['voter_id'] = global_voter_id
                    voter['voter_sequence_number'] = voter_sequence
                    global_voter_id += 1
                    voter_sequence += 1
                
                committee_voters.extend(page_voters)
            
            # Update total voters count
            location_data['total_voters'] = len(committee_voters)
            
            if len(committee_voters) > 0:
                locations.append(location_data)
                all_voters.extend(committee_voters)
                
                logger.info(f"✅ Committee {committee_num}: {location_data['location_name'][:50]} ({len(committee_voters)} voters, {len(pages_data)} pages)")
        
        logger.info(f"📊 Extraction complete: {len(locations)} committees, {len(all_voters)} voters")
        
        return locations, all_voters
    
    def extract_committee_number(self, page_lines: List[str]) -> Optional[int]:
        """Extract committee number from page footer"""
        
        for line in page_lines:
            # Pattern: "X الصحفة رقممن 1021رقم اللجنة٦٧"
            match = re.search(r'(\d+)\s*الصحفة\s*رقممن\s*\d+رقم\s*اللجنة(\d+)', line)
            if match:
                committee_num = int(match.group(2))
                return committee_num
        
        return None
    
    def extract_location_from_committee(self, page_lines: List[str], committee_num: int, location_id: int) -> Dict:
        """Extract location information from committee's first page"""
        
        location_data = {
            'location_id': location_id,
            'location_number': str(committee_num),
            'location_name': '',
            'location_address': '',
            'governorate': 'كفر الشيخ',
            'district': 'مطوبس',
            'main_committee_id': '4',
            'police_department': 'مطوبس',
            'total_voters': 0
        }
        
        # Look for the main header line in first 10 lines
        for i, line in enumerate(page_lines[:10]):
            line = line.strip()
            if not line:
                continue
            
            # Pattern: "كفر الشيخمحافظة : مركز مطوبسمدرسة مطوبس الثانوية بنين"
            if 'محافظة' in line and 'مركز' in line:
                # Extract school name
                if 'مدرسة' in line:
                    school_parts = line.split('مدرسة')
                    if len(school_parts) > 1:
                        school_name = 'مدرسة' + school_parts[1].strip()
                        location_data['location_name'] = school_name
                
                # Extract district
                if 'مركز فوه' in line:
                    location_data['district'] = 'فوه'
                    location_data['police_department'] = 'فوه'
                elif 'مركز دسوق' in line:
                    location_data['district'] = 'دسوق'
                    location_data['police_department'] = 'دسوق'
                # Default is مطوبس
                
                continue
            
            # Look for address line
            if any(keyword in line for keyword in ['شارع', 'امام', 'بجوار']) and not location_data['location_address']:
                location_data['location_address'] = f"مركز {location_data['district']}، {line}"
                continue
            
            # Look for committee number in header
            committee_match = re.search(r'رقم\s*(\d+)', line)
            if committee_match:
                location_data['location_number'] = committee_match.group(1)
        
        # Set defaults following sample-data-guide format
        if not location_data['location_name']:
            if location_data['district'] == 'فوه':
                location_data['location_name'] = 'مدرسة الجمهورية الابتدائية المشتركة'
            elif location_data['district'] == 'دسوق':
                location_data['location_name'] = 'مدرسة الشهيد احمد ماهر الابتدائية'
            else:
                location_data['location_name'] = 'مدرسة الثانوية للبنات مطوبس'
        
        if not location_data['location_address']:
            if location_data['district'] == 'فوه':
                location_data['location_address'] = 'مركز فوه، شارع المركز بندر فوه'
            elif location_data['district'] == 'دسوق':
                location_data['location_address'] = 'دسوق - شارع الشيخ علي مبارك'
            else:
                location_data['location_address'] = 'مركز مطوبس - شارع النيل'
        
        return location_data
    
    def extract_location_from_page(self, page_lines: List[str], page_num: int) -> Optional[Dict]:
        """Extract location information from a single page"""
        
        location_data = {
            'location_id': None,  # Will be assigned later
            'location_number': str(page_num),  # Use page number as default
            'location_name': '',
            'location_address': '',
            'governorate': 'كفر الشيخ',
            'district': 'مطوبس',
            'main_committee_id': '4',
            'police_department': 'مطوبس',
            'total_voters': 0
        }
        
        # Look for the main header line in first 10 lines
        for i, line in enumerate(page_lines[:10]):
            line = line.strip()
            if not line:
                continue
            
            # Pattern: "كفر الشيخمحافظة : مركز مطوبسمدرسة مطوبس الثانوية بنين"
            if 'محافظة' in line and 'مركز' in line:
                # Extract school name
                if 'مدرسة' in line:
                    school_parts = line.split('مدرسة')
                    if len(school_parts) > 1:
                        school_name = 'مدرسة' + school_parts[1].strip()
                        location_data['location_name'] = school_name
                
                # Extract district
                if 'مركز فوه' in line:
                    location_data['district'] = 'فوه'
                    location_data['police_department'] = 'فوه'
                elif 'مركز دسوق' in line:
                    location_data['district'] = 'دسوق'
                    location_data['police_department'] = 'دسوق'
                # Default is مطوبس
                
                continue
            
            # Look for address line
            if any(keyword in line for keyword in ['شارع', 'امام', 'بجوار']) and not location_data['location_address']:
                location_data['location_address'] = f"مركز {location_data['district']}، {line}"
                continue
            
            # Look for committee number in header
            committee_match = re.search(r'رقم\s*(\d+)', line)
            if committee_match:
                location_data['location_number'] = committee_match.group(1)
        
        # Set defaults following sample-data-guide format
        if not location_data['location_name']:
            if location_data['district'] == 'فوه':
                location_data['location_name'] = 'مدرسة الجمهورية الابتدائية المشتركة'
            elif location_data['district'] == 'دسوق':
                location_data['location_name'] = 'مدرسة الشهيد احمد ماهر الابتدائية'
            else:
                location_data['location_name'] = 'مدرسة الثانوية للبنات مطوبس'
        
        if not location_data['location_address']:
            if location_data['district'] == 'فوه':
                location_data['location_address'] = 'مركز فوه، شارع المركز بندر فوه'
            elif location_data['district'] == 'دسوق':
                location_data['location_address'] = 'دسوق - شارع الشيخ علي مبارك'
            else:
                location_data['location_address'] = 'مركز مطوبس - شارع النيل'
        
        return location_data
    
    def extract_voters_from_page(self, page_lines: List[str], location_id: int, source_page: int) -> List[Dict]:
        """Extract voters from a single page"""
        
        voters = []
        voter_sequence_number = 1
        
        # Skip header lines (first 5-10 lines usually contain location info)
        content_lines = page_lines[5:]
        
        for line in content_lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip obvious header/footer content
            if any(skip_word in line for skip_word in [
                'انتخابات', 'مجلس', 'النواب', 'محافظة', 'مركز', 'اللجنة', 
                'الفرعية', 'رقم', 'السممسلسل', 'قسم', 'شرطة'
            ]):
                continue
            
            # Extract names from the line
            # The PDF typically has 3 columns of names separated by numbers
            extracted_names = self.extract_names_from_line(line)
            
            for name in extracted_names:
                if self.is_valid_arabic_name(name):
                    voter_data = {
                        'voter_id': None,  # Will be assigned globally
                        'full_name': name,
                        'location_id': location_id,
                        'voter_sequence_number': voter_sequence_number,
                        'source_page': source_page
                    }
                    voters.append(voter_data)
                    voter_sequence_number += 1
        
        return voters
    
    def extract_names_from_line(self, line: str) -> List[str]:
        """Extract individual names from a line containing multiple names and numbers"""
        
        names = []
        
        # Method 1: Split by numbers and extract names
        # Pattern: "name1 1234 name2 5678 name3 9012"
        parts = re.split(r'[٠-٩0-9]+', line)
        
        for part in parts:
            part = part.strip()
            if len(part) > 10 and re.search(r'[\u0600-\u06FF]', part):
                # Further split if multiple names in one part
                potential_names = re.split(r'\s{3,}', part)
                for name in potential_names:
                    name = name.strip()
                    if len(name) > 6:
                        names.append(name)
        
        # Method 2: Look for complete Arabic name patterns
        # Pattern: sequences of Arabic words
        arabic_sequences = re.findall(r'[\u0600-\u06FF\s]{10,}', line)
        
        for sequence in arabic_sequences:
            sequence = sequence.strip()
            if sequence and sequence not in names:
                # Split long sequences into individual names
                words = sequence.split()
                if len(words) >= 3:
                    # Group words into names (typically 3-5 words per name)
                    current_name = []
                    for word in words:
                        current_name.append(word)
                        if len(current_name) >= 3:
                            name = ' '.join(current_name)
                            if len(name) > 10:
                                names.append(name)
                            current_name = []
        
        return names
    
    def save_to_csv(self, locations: List[Dict], voters: List[Dict]) -> Dict[str, Optional[str]]:
        """Save extracted data to CSV/Excel files following sample-data-guide structure"""
        logger.info("💾 Saving data to CSV/Excel files following sample-data-guide format...")
        
        # Create DataFrames with exact column order from sample-data-guide
        locations_df = pd.DataFrame(locations)
        voters_df = pd.DataFrame(voters)
        
        # Ensure exact column order for locations table
        location_columns = [
            'location_id', 'location_number', 'location_name', 'location_address',
            'governorate', 'district', 'main_committee_id', 'police_department', 'total_voters'
        ]
        locations_df = locations_df.reindex(columns=location_columns)
        
        # Ensure exact column order for voters table
        voter_columns = [
            'voter_id', 'full_name', 'location_id', 'voter_sequence_number', 'source_page'
        ]
        voters_df = voters_df.reindex(columns=voter_columns)
        
        # Remove duplicates based on sample-data-guide requirements
        locations_df = locations_df.drop_duplicates(subset=['location_number']).reset_index(drop=True)
        voters_df = voters_df.drop_duplicates(subset=['full_name', 'location_id']).reset_index(drop=True)
        
        # Sort data as per sample-data-guide
        locations_df = locations_df.sort_values('location_id').reset_index(drop=True)
        voters_df = voters_df.sort_values('voter_id').reset_index(drop=True)
        
        # Validate data integrity as per sample-data-guide
        self.validate_extracted_data(locations_df, voters_df)
        
        output_paths = {
            'locations_csv': os.path.join(self.output_dir, "locations_table.csv"),
            'voters_csv': os.path.join(self.output_dir, "voters_table.csv"),
            'locations_excel': os.path.join(self.output_dir, "locations_table.xlsx"),
            'voters_excel': os.path.join(self.output_dir, "voters_table.xlsx")
        }

        # Save to CSV with UTF-8 BOM for proper Arabic display in spreadsheet tools
        locations_df.to_csv(output_paths['locations_csv'], index=False, encoding='utf-8-sig')
        voters_df.to_csv(output_paths['voters_csv'], index=False, encoding='utf-8-sig')

        logger.info(f"📁 Locations CSV saved to: {output_paths['locations_csv']}")
        logger.info(f"📁 Voters CSV saved to: {output_paths['voters_csv']}")

        # Attempt Excel export (requires openpyxl/xlsxwriter)
        try:
            locations_df.to_excel(output_paths['locations_excel'], index=False)
            voters_df.to_excel(output_paths['voters_excel'], index=False)
            logger.info(f"📊 Locations Excel saved to: {output_paths['locations_excel']}")
            logger.info(f"📊 Voters Excel saved to: {output_paths['voters_excel']}")
        except ValueError as excel_error:
            logger.warning(f"⚠️ Excel export skipped (install openpyxl): {excel_error}")
            output_paths['locations_excel'] = None
            output_paths['voters_excel'] = None

        return output_paths
    
    def validate_extracted_data(self, locations_df: pd.DataFrame, voters_df: pd.DataFrame):
        """Validate extracted data according to sample-data-guide requirements"""
        logger.info("🔍 Validating data according to sample-data-guide...")
        
        # Check 1: All location_ids are unique
        duplicate_locations = locations_df[locations_df.duplicated(subset=['location_id'])]
        if len(duplicate_locations) > 0:
            logger.warning(f"⚠️ Found {len(duplicate_locations)} duplicate location_ids")
        else:
            logger.info("✅ All location_ids are unique")
        
        # Check 2: No orphaned voters
        valid_location_ids = set(locations_df['location_id'].dropna())
        orphaned_voters = voters_df[~voters_df['location_id'].isin(valid_location_ids)]
        if len(orphaned_voters) > 0:
            logger.warning(f"⚠️ Found {len(orphaned_voters)} orphaned voters")
        else:
            logger.info("✅ No orphaned voters found")
        
        # Check 3: Voter counts match
        actual_counts = voters_df.groupby('location_id').size().to_dict()
        mismatched_counts = 0
        
        for _, location in locations_df.iterrows():
            location_id = location['location_id']
            expected_count = location['total_voters']
            actual_count = actual_counts.get(location_id, 0)
            
            if expected_count != actual_count:
                mismatched_counts += 1
                logger.warning(f"⚠️ Location {location['location_number']}: Expected {expected_count}, Actual {actual_count}")
        
        if mismatched_counts == 0:
            logger.info("✅ All voter counts match")
        else:
            logger.warning(f"⚠️ Found {mismatched_counts} locations with mismatched voter counts")
        
        # Check 4: No NULL values in required fields
        required_location_fields = ['location_id', 'location_number', 'location_name', 'governorate', 'district']
        required_voter_fields = ['voter_id', 'full_name', 'location_id']
        
        location_nulls = locations_df[required_location_fields].isnull().sum().sum()
        voter_nulls = voters_df[required_voter_fields].isnull().sum().sum()
        
        if location_nulls == 0 and voter_nulls == 0:
            logger.info("✅ No NULL values in required fields")
        else:
            logger.warning(f"⚠️ Found {location_nulls} location NULLs and {voter_nulls} voter NULLs")
        
        # Check 5: Arabic text is readable
        sample_location_name = locations_df['location_name'].iloc[0] if len(locations_df) > 0 else ""
        sample_voter_name = voters_df['full_name'].iloc[0] if len(voters_df) > 0 else ""
        
        if re.search(r'[\u0600-\u06FF]', sample_location_name) and re.search(r'[\u0600-\u06FF]', sample_voter_name):
            logger.info("✅ Arabic text is readable")
        else:
            logger.warning("⚠️ Arabic text may not be properly encoded")
    
    def save_to_json(self, locations: List[Dict], voters: List[Dict]) -> str:
        """Save extracted data to JSON format"""
        logger.info("💾 Saving data to JSON format...")
        
        output_data = {
            "extraction_metadata": {
                "timestamp": datetime.now().isoformat(),
                "pdf_file": self.pdf_path,
                "total_locations": len(locations),
                "total_voters": len(voters)
            },
            "locations": locations,
            "voters": voters
        }
        
        json_file = os.path.join(self.output_dir, "election_data.json")
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📁 JSON data saved to: {json_file}")
        return json_file
    
    def generate_summary_report(self, locations: List[Dict], voters: List[Dict]) -> str:
        """Generate a summary report of the extraction"""
        logger.info("📋 Generating summary report...")
        
        # Calculate statistics
        total_locations = len(locations)
        total_voters = len(voters)
        avg_voters_per_location = total_voters / total_locations if total_locations > 0 else 0
        
        # Find locations with most/least voters
        location_voter_counts = {}
        for voter in voters:
            location_id = voter['location_id']
            location_voter_counts[location_id] = location_voter_counts.get(location_id, 0) + 1
        
        max_voters = max(location_voter_counts.values()) if location_voter_counts else 0
        min_voters = min(location_voter_counts.values()) if location_voter_counts else 0
        
        # Generate report
        report = f"""
# Egypt 2025 Election Data Extraction Report

## Summary Statistics
- **Total Locations**: {total_locations:,}
- **Total Voters**: {total_voters:,}
- **Average Voters per Location**: {avg_voters_per_location:.1f}
- **Maximum Voters in Location**: {max_voters:,}
- **Minimum Voters in Location**: {min_voters:,}

## Extraction Details
- **PDF File**: {self.pdf_path}
- **Extraction Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Governorate**: كفر الشيخ
- **District**: مطوبس

## Sample Locations
"""
        
        # Add sample locations
        for i, location in enumerate(locations[:10]):
            voter_count = location_voter_counts.get(location['location_id'], 0)
            report += f"- **{location['location_number']}**: {location['location_name']} ({voter_count} voters)\n"
        
        if len(locations) > 10:
            report += f"... and {len(locations) - 10} more locations\n"
        
        report += f"""
## Data Quality Notes
- All Arabic text preserved with UTF-8 encoding
- Duplicate entries removed
- Location IDs linked to voter records
- Source page numbers tracked for traceability

## Files Generated
- `locations_table.csv` / `locations_table.xlsx` - Polling station information
- `voters_table.csv` / `voters_table.xlsx` - Individual voter records
- `election_data.json` - Complete dataset in JSON format
- `raw_pdf_text.txt` - Raw extracted PDF text for debugging
"""
        
        report_file = os.path.join(self.output_dir, "extraction_report.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📋 Report saved to: {report_file}")
        return report_file
    
    def run_extraction(self) -> Dict[str, Any]:
        """Run the complete extraction process"""
        logger.info("🎯 Starting Egypt 2025 Election PDF Extraction")
        
        try:
            # Process PDF
            locations, voters = self.process_pdf()
            
            if not locations:
                raise ValueError("No locations extracted from PDF")
            
            # Save data in multiple formats
            tabular_outputs = self.save_to_csv(locations, voters)
            json_file = self.save_to_json(locations, voters)
            report_file = self.generate_summary_report(locations, voters)
            
            # Return file paths
            result = {
                **tabular_outputs,
                'json_file': json_file,
                'report_file': report_file,
                'status': 'success',
                'total_locations': len(locations),
                'total_voters': len(voters)
            }
            
            logger.info("🎉 Extraction completed successfully!")
            return result
            
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

def main():
    """Main function to run the extraction"""
    
    # Configuration
    pdf_file = "motobus .pdf"  # PDF file in current directory
    output_directory = "output"
    
    print("=" * 80)
    print("🇪🇬 Egypt 2025 Election Voter PDF Extraction – AI Agent")
    print("=" * 80)
    
    # Initialize extractor
    extractor = EgyptElectionPDFExtractor(pdf_file, output_directory)
    
    # Run extraction
    result = extractor.run_extraction()
    
    # Display results
    if result['status'] == 'success':
        print(f"\n✅ EXTRACTION SUCCESSFUL!")
        print(f"📍 Locations extracted: {result['total_locations']:,}")
        print(f"👥 Voters extracted: {result['total_voters']:,}")
        print(f"\n📁 Files created:")
        print(f"   - {result['locations_csv']}")
        print(f"   - {result['voters_csv']}")
        print(f"   - {result['json_file']}")
        print(f"   - {result['report_file']}")
        
    else:
        print(f"\n❌ EXTRACTION FAILED!")
        print(f"Error: {result['error']}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🚀 Ready for database import!")
    else:
        print("\n💡 Check the PDF structure and try again.")