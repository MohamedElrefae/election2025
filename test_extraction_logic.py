#!/usr/bin/env python3
"""
Test script for Egypt 2025 Election PDF Extraction logic
Tests the extraction patterns and validates data structure
"""

import re
import json
from typing import List, Dict

def test_arabic_name_patterns():
    """Test Arabic name extraction patterns"""
    print("🔍 Testing Arabic name extraction patterns...")
    
    # Sample Arabic names from your data
    test_names = [
        "ابتسام احمد محمد قبط يونس",
        "ابتسام احمد السيد فتح الله القله",
        "محمد عبد الله احمد حسن",
        "فاطمة محمود علي السيد",
        "احمد محمد عبد الرحمن"
    ]
    
    # Pattern for Arabic names
    arabic_name_pattern = r'[\u0600-\u06FF\s]+'
    
    for name in test_names:
        match = re.search(arabic_name_pattern, name)
        if match:
            print(f"   ✅ {name}")
        else:
            print(f"   ❌ {name}")
    
    print()

def test_location_number_patterns():
    """Test location number extraction patterns"""
    print("🔍 Testing location number patterns...")
    
    # Sample location patterns from your data
    test_lines = [
        "77",
        "78", 
        "81 الصحفة رقممن 1021رقم اللجنة٨٧",
        "92 مدرسة عبدالحميد شلبى الابتدائية",
        "110 مدرسة الجمهورية الابتدائية المشتركة"
    ]
    
    patterns = [
        r'^\d{1,3}$',  # Standalone numbers
        r'(\d{1,3})\s*الصحفة\s*رقممن\s*\d+رقم\s*اللجنة(\d+)',  # Committee pattern
        r'^(\d{1,3})\s+(.+)'  # Number followed by text
    ]
    
    for line in test_lines:
        print(f"   Testing: {line}")
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, line)
            if match:
                print(f"      ✅ Pattern {i+1}: {match.groups() if match.groups() else match.group(0)}")
            else:
                print(f"      ❌ Pattern {i+1}: No match")
        print()

def test_school_name_patterns():
    """Test school name extraction patterns"""
    print("🔍 Testing school name patterns...")
    
    # Sample school names
    test_schools = [
        "مدرسة عبدالحميد شلبى الابتدائية",
        "مدرسة الجمهورية الابتدائية المشتركة",
        "الثانوية العامة للبنين",
        "مدرسة النصر للتعليم الأساسي",
        "العدادية المشتركة"
    ]
    
    school_patterns = [
        r'مدرسة\s+[\u0600-\u06FF\s]+',
        r'[\u0600-\u06FF\s]*الثانوية[\u0600-\u06FF\s]*',
        r'[\u0600-\u06FF\s]*الابتدائية[\u0600-\u06FF\s]*',
        r'[\u0600-\u06FF\s]*للتعليم[\u0600-\u06FF\s]*',
        r'[\u0600-\u06FF\s]*العدادية[\u0600-\u06FF\s]*'
    ]
    
    for school in test_schools:
        print(f"   Testing: {school}")
        
        for i, pattern in enumerate(school_patterns):
            match = re.search(pattern, school)
            if match:
                print(f"      ✅ Pattern {i+1}: {match.group(0)}")
                break
        else:
            print(f"      ❌ No pattern matched")
        print()

def test_address_patterns():
    """Test address extraction patterns"""
    print("🔍 Testing address patterns...")
    
    # Sample addresses
    test_addresses = [
        "مركز مطوبس",
        "مركز فوه، شارع المركز بندر فوه",
        "شارع الجمهورية",
        "قرية الصالحية",
        "امام المسجد الكبير",
        "بجوار محطة القطار"
    ]
    
    address_patterns = [
        r'مركز\s+[\u0600-\u06FF\s]+',
        r'شارع\s+[\u0600-\u06FF\s]+',
        r'قرية\s+[\u0600-\u06FF\s]+',
        r'امام\s+[\u0600-\u06FF\s]+',
        r'بجوار\s+[\u0600-\u06FF\s]+'
    ]
    
    for address in test_addresses:
        print(f"   Testing: {address}")
        
        for i, pattern in enumerate(address_patterns):
            match = re.search(pattern, address)
            if match:
                print(f"      ✅ Pattern {i+1}: {match.group(0)}")
                break
        else:
            print(f"      ❌ No pattern matched")
        print()

def test_sample_data_structure():
    """Test the sample data structure from your specifications"""
    print("🔍 Testing sample data structure...")
    
    # Sample data based on your specifications
    sample_locations = [
        {
            'location_id': 1,
            'location_number': '110',
            'location_name': 'مدرسة الجمهورية الابتدائية المشتركة',
            'location_address': 'مركز فوه، شارع المركز بندر فوه',
            'governorate': 'كفر الشيخ',
            'district': 'فوه',
            'main_committee_id': '4',
            'police_department': 'فوه',
            'total_voters': 1350
        }
    ]
    
    sample_voters = [
        {
            'voter_id': 1,
            'full_name': 'ابتسام احمد محمد قبط يونس',
            'location_id': 1,
            'source_page': 1
        },
        {
            'voter_id': 2,
            'full_name': 'ابتسام احمد السيد فتح الله القله',
            'location_id': 1,
            'source_page': 1
        }
    ]
    
    print("   Sample Locations:")
    for location in sample_locations:
        print(f"      ✅ ID: {location['location_id']}, Number: {location['location_number']}")
        print(f"         Name: {location['location_name']}")
        print(f"         Address: {location['location_address']}")
        print(f"         Voters: {location['total_voters']}")
    
    print("\n   Sample Voters:")
    for voter in sample_voters:
        print(f"      ✅ ID: {voter['voter_id']}, Name: {voter['full_name']}")
        print(f"         Location: {voter['location_id']}, Page: {voter['source_page']}")
    
    print()

def test_data_validation():
    """Test data validation logic"""
    print("🔍 Testing data validation logic...")
    
    # Test valid Arabic names
    valid_names = [
        "محمد احمد علي",
        "فاطمة محمود السيد",
        "عبد الله محمد حسن"
    ]
    
    # Test invalid names
    invalid_names = [
        "123",
        "abc def",
        "محمد",  # Too short
        ""
    ]
    
    def validate_arabic_name(name: str) -> bool:
        """Validate Arabic name"""
        if not name or len(name.strip()) < 3:
            return False
        
        words = name.strip().split()
        if len(words) < 2:
            return False
        
        # Check if contains Arabic characters
        if not re.search(r'[\u0600-\u06FF]', name):
            return False
        
        return True
    
    print("   Valid names:")
    for name in valid_names:
        result = validate_arabic_name(name)
        print(f"      {'✅' if result else '❌'} {name}")
    
    print("\n   Invalid names:")
    for name in invalid_names:
        result = validate_arabic_name(name)
        print(f"      {'✅' if result else '❌'} {name}")
    
    print()

def test_csv_structure():
    """Test CSV output structure"""
    print("🔍 Testing CSV output structure...")
    
    # Expected columns for locations table
    expected_location_columns = [
        'location_id', 'location_number', 'location_name', 
        'location_address', 'governorate', 'district', 
        'main_committee_id', 'police_department', 'total_voters'
    ]
    
    # Expected columns for voters table
    expected_voter_columns = [
        'voter_id', 'full_name', 'location_id', 'source_page'
    ]
    
    print("   Expected Locations CSV columns:")
    for i, col in enumerate(expected_location_columns, 1):
        print(f"      {i:2d}. {col}")
    
    print("\n   Expected Voters CSV columns:")
    for i, col in enumerate(expected_voter_columns, 1):
        print(f"      {i:2d}. {col}")
    
    print()

def main():
    """Run all tests"""
    print("=" * 70)
    print("🧪 Egypt 2025 Election PDF Extraction - Logic Tests")
    print("=" * 70)
    print()
    
    # Run all tests
    test_arabic_name_patterns()
    test_location_number_patterns()
    test_school_name_patterns()
    test_address_patterns()
    test_sample_data_structure()
    test_data_validation()
    test_csv_structure()
    
    print("=" * 70)
    print("✅ All extraction logic tests completed!")
    print("💡 These patterns will be used in the main extraction script")
    print("=" * 70)

if __name__ == "__main__":
    main()