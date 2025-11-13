
# Egypt 2025 Election Data Extraction Report

## Summary Statistics
- **Total Locations**: 34
- **Total Voters**: 337,729
- **Average Voters per Location**: 9933.2
- **Maximum Voters in Location**: 18,648
- **Minimum Voters in Location**: 3,518

## Extraction Details
- **PDF File**: motobus .pdf
- **Extraction Date**: 2025-11-12 20:33:05
- **Governorate**: كفر الشيخ
- **District**: مطوبس

## Sample Locations
- **1**: مدرسةالجزيرة الخضراء الثانوية التجارية (7720 voters)
- **8**: مدرسةالسعاده للتعليم الساسى (4983 voters)
- **9**: مدرسةالشهيد البطل على محمد فهمى فليفل البتدائية (10947 voters)
- **18**: مدرسةالقنى البتدائية المشتركة (9027 voters)
- **19**: مدرسةمعدية مهدى تعليم اساسى (3518 voters)
- **28**: مدرسةالمنار البتدائية (13660 voters)
- **29**: مدرسةعبدالحميد شلبى البتدائية (7210 voters)
- **38**: مدرسةالغنايم للتعليم الساسى (13483 voters)
- **39**: مدرسةالخليج العدادية بنات (11902 voters)
- **48**: مدرسةالشهيد/ رضا صبرى محمد فراج للتعليم الساسى (11548 voters)
... and 24 more locations

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
