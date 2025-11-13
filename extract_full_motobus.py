import PyPDF2
import pandas as pd
import re
from pathlib import Path
import json
import time

def extract_full_motobus_data():
    pdf_path = 'motobus .pdf'
    print('Starting FULL motobus PDF extraction...')
    
    locations = []
    voters = []
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        total_pages = len(pdf_reader.pages)
        print(f'Processing ALL {total_pages} pages...')
        
        start_time = time.time()
        
        for page_num in range(total_pages):
            if page_num % 100 == 0:
                elapsed = time.time() - start_time
                print(f'Processing page {page_num + 1}/{total_pages} ({elapsed:.1f}s elapsed)')
            
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            if not text.strip():
                continue
                
            # Extract location info
            location_info = {
                'location_id': page_num + 1,
                'location_number': str(page_num + 1),
                'location_name': '',
                'location_address': '',
                'governorate': 'كفر الشيخ',
                'district': 'مطوبس',
                'main_committee_id': '',
                'police_department': '',
                'total_voters': 0
            }
            
            # Extract committee number
            committee_match = re.search(r'اللجنة الفرعية رقم\s*(\d+)', text)
            if committee_match:
                location_info['location_number'] = committee_match.group(1)
            
            # Extract school name
            school_match = re.search(r'مدرسة\s*([^\n]+)', text)
            if school_match:
                location_info['location_name'] = school_match.group(1).strip()
            
            # Extract address
            address_match = re.search(r'شارع\s*([^\n]+)', text)
            if address_match:
                location_info['location_address'] = address_match.group(1).strip()
            
            # Extract main committee
            main_committee_match = re.search(r'للجنة العامة رقم\s*:\s*(\d+)', text)
            if main_committee_match:
                location_info['main_committee_id'] = main_committee_match.group(1)
            
            # Extract voters
            page_voters = []
            lines = text.split('\n')
            voter_id = 1
            
            for line in lines:
                # Look for Arabic names (improved pattern)
                names = re.findall(r'[أ-ي][أ-ي\s]{8,}[أ-ي]', line)
                for name in names:
                    name = re.sub(r'\s+', ' ', name.strip())
                    if len(name) > 10 and not any(word in name for word in ['مدرسة', 'شارع', 'محافظة', 'مركز', 'اللجنة', 'انتخابات']):
                        page_voters.append({
                            'voter_id': voter_id,
                            'full_name': name,
                            'location_id': location_info['location_id'],
                            'source_page': page_num + 1
                        })
                        voter_id += 1
            
            location_info['total_voters'] = len(page_voters)
            locations.append(location_info)
            voters.extend(page_voters)
    
    # Export results
    Path('output').mkdir(exist_ok=True)
    
    print('Exporting to CSV...')
    pd.DataFrame(locations).to_csv('output/locations_full.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame(voters).to_csv('output/voters_full.csv', index=False, encoding='utf-8-sig')
    
    print('Exporting to JSON...')
    data = {
        'locations': locations, 
        'voters': voters,
        'metadata': {
            'total_locations': len(locations),
            'total_voters': len(voters),
            'extraction_date': pd.Timestamp.now().isoformat(),
            'source_file': 'motobus .pdf'
        }
    }
    with open('output/voter_data_full.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Generate SQL
    print('Generating SQL...')
    with open('output/voter_data_full.sql', 'w', encoding='utf-8') as f:
        f.write('''-- Egypt 2025 Election Voter Database - Motobus District
CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY,
    location_number VARCHAR(50),
    location_name TEXT,
    location_address TEXT,
    governorate VARCHAR(100),
    district VARCHAR(100),
    main_committee_id VARCHAR(50),
    police_department VARCHAR(100),
    total_voters INTEGER
);

CREATE TABLE IF NOT EXISTS voters (
    voter_id INTEGER,
    full_name TEXT NOT NULL,
    location_id INTEGER,
    source_page INTEGER,
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- Insert locations data
''')
        
        for location in locations:
            values = [
                str(location['location_id']),
                f\"'{location['location_number']}\",
                f\"'{location['location_name'].replace(chr(39), chr(39)+chr(39))}\",
                f\"'{location['location_address'].replace(chr(39), chr(39)+chr(39))}\",
                f\"'{location['governorate']}\",
                f\"'{location['district']}\",
                f\"'{location['main_committee_id']}\",
                f\"'{location['police_department']}\",
                str(location['total_voters'])
            ]
            f.write(f\"INSERT INTO locations VALUES ({', '.join(values)});\\n\")
        
        f.write(\"\\n-- Insert voters data\\n\")
        for voter in voters:
            values = [
                str(voter['voter_id']),
                f\"'{voter['full_name'].replace(chr(39), chr(39)+chr(39))}\",
                str(voter['location_id']),
                str(voter['source_page'])
            ]
            f.write(f\"INSERT INTO voters VALUES ({', '.join(values)});\\n\")
    
    # Summary report
    with open('output/extraction_report_full.txt', 'w', encoding='utf-8') as f:
        f.write('Egypt 2025 Election PDF Extraction Report - Motobus District\\n')
        f.write('=' * 60 + '\\n\\n')
        f.write(f'Total Locations: {len(locations)}\\n')
        f.write(f'Total Voters: {len(voters)}\\n')
        f.write(f'Average Voters per Location: {len(voters)/len(locations):.1f}\\n\\n')
        f.write(f'Governorate: كفر الشيخ\\n')
        f.write(f'District: مطوبس\\n\\n')
        f.write(f'Extraction completed: {pd.Timestamp.now()}\\n')
    
    total_time = time.time() - start_time
    print(f'\\nFULL EXTRACTION COMPLETE!')
    print(f'Time taken: {total_time:.1f} seconds')
    print(f'Found {len(locations)} locations and {len(voters)} voters')
    print('Results saved to output/ directory with _full suffix')
    
    return locations, voters

if __name__ == '__main__':
    extract_full_motobus_data()
