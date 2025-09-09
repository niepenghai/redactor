#!/usr/bin/env python3
"""
Test the updated patterns to see if they can detect names and addresses.
"""

import re
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.patterns import get_financial_patterns
from utils.realistic_generators import RealisticDataGenerator

def test_patterns():
    """Test the patterns against sample text."""
    
    # Test text with the names and address from user's example
    test_text = """
    XIA LIN
    QIZHI CHEN
    2601 CHOCOLATE ST
    PLEASANTON CA 94588-8436
    
    John Smith lives at 123 Main Street
    Contact: jane.doe@email.com
    Phone: (555) 123-4567
    SSN: 123-45-6789
    """
    
    print("🔍 Testing Pattern Recognition")
    print("=" * 50)
    print("Test text:")
    print(test_text)
    print("\n" + "=" * 50)
    
    # Get patterns
    patterns = get_financial_patterns()
    
    # Initialize realistic generator
    config = {
        "replacement_mode": "realistic",
        "replacement_settings": {
            "use_consistent_replacements": True,
            "realistic_addresses": {
                "streets": ["456 Oak Ave", "789 Pine Rd"],
                "cities_states": ["Springfield, IL", "Franklin, TX"]
            }
        }
    }
    generator = RealisticDataGenerator(config)
    
    # Test each pattern category
    total_matches = 0
    for category, pattern_list in patterns.items():
        print(f"\n📋 Testing {category}:")
        category_matches = 0
        
        for pattern, replacement in pattern_list:
            matches = list(re.finditer(pattern, test_text, re.IGNORECASE))
            
            for match in matches:
                original = match.group()
                
                # Generate realistic replacement
                if hasattr(generator, f'generate_{category}'):
                    realistic_replacement = getattr(generator, f'generate_{category}')(original)
                else:
                    realistic_replacement = replacement
                
                print(f"  ✅ Found: '{original}' → '{realistic_replacement}'")
                category_matches += 1
                total_matches += 1
        
        if category_matches == 0:
            print(f"  ❌ No matches found for {category}")
    
    print(f"\n📊 Total matches found: {total_matches}")
    
    # Test specific cases
    print("\n🎯 Testing specific examples:")
    
    # Test the exact names from user's example
    name_patterns = patterns['names']
    for pattern, replacement in name_patterns:
        # Test XIA LIN
        if re.search(pattern, "XIA LIN"):
            realistic_name = generator.generate_person_name("XIA LIN")
            print(f"  ✅ 'XIA LIN' → '{realistic_name}'")
        
        # Test QIZHI CHEN
        if re.search(pattern, "QIZHI CHEN"):
            realistic_name = generator.generate_person_name("QIZHI CHEN")
            print(f"  ✅ 'QIZHI CHEN' → '{realistic_name}'")
    
    # Test the address
    address_patterns = patterns['address']
    for pattern, replacement in address_patterns:
        if re.search(pattern, "2601 CHOCOLATE ST"):
            realistic_address = generator.generate_address("2601 CHOCOLATE ST")
            print(f"  ✅ '2601 CHOCOLATE ST' → '{realistic_address}'")
        
        if re.search(pattern, "PLEASANTON CA 94588-8436"):
            realistic_address = generator.generate_address("PLEASANTON CA 94588-8436")
            print(f"  ✅ 'PLEASANTON CA 94588-8436' → '{realistic_address}'")

if __name__ == "__main__":
    test_patterns()