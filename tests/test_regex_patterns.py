#!/usr/bin/env python3
"""
Test name recognition patterns specifically for the examples mentioned.
"""

import re
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.patterns import get_financial_patterns

def test_name_recognition():
    """Test name recognition with specific examples."""
    
    print("🔍 Name Recognition Pattern Testing")
    print("=" * 50)
    
    # Test cases including the specific examples mentioned
    test_cases = [
        "XIA LIN",
        "QIZHI CHEN", 
        "John Smith",
        "Mary Johnson",
        "Dr. Michael Brown",
        "Account Holder: XIA LIN",
        "Customer: QIZHI CHEN",
        "Signature: John Smith",
        # False positives to avoid
        "Main Street",  # Should NOT match
        "Oak Avenue",   # Should NOT match  
        "CA 94588",     # Should NOT match
        "ST AVE",       # Should NOT match
        "Wells Fargo",  # Should NOT match
    ]
    
    patterns = get_financial_patterns()['names']
    
    print(f"📋 Testing {len(test_cases)} cases with {len(patterns)} patterns:")
    print()
    
    for test_text in test_cases:
        print(f"Testing: '{test_text}'")
        matched = False
        
        for i, (pattern, replacement) in enumerate(patterns, 1):
            match = re.search(pattern, test_text, re.IGNORECASE)
            if match:
                matched_text = match.group()
                print(f"  ✅ Pattern {i}: '{matched_text}' → {replacement}")
                matched = True
        
        if not matched:
            # Check if this should be a match or correctly rejected
            should_match = any(name in test_text for name in ["XIA LIN", "QIZHI CHEN", "John Smith", "Mary Johnson", "Michael Brown"])
            if should_match:
                print(f"  ❌ Should have matched but didn't!")
            else:
                print(f"  ✅ Correctly rejected (not a name)")
        
        print()
    
    # Test full document context
    print("📄 Testing in document context:")
    print("-" * 30)
    
    sample_document = """
    XIA LIN
    QIZHI CHEN
    2601 CHOCOLATE ST
    PLEASANTON CA 94588-8436
    
    Account Summary for John Smith
    Wells Fargo Bank
    Customer Service: (800) 742-4932
    
    Dr. Michael Brown
    123 Main Street
    """
    
    print("Sample document:")
    print(sample_document)
    print("\nName matches found:")
    
    all_matches = []
    for i, (pattern, replacement) in enumerate(patterns, 1):
        matches = list(re.finditer(pattern, sample_document, re.IGNORECASE | re.MULTILINE))
        for match in matches:
            all_matches.append({
                'pattern': i,
                'text': match.group(),
                'replacement': replacement,
                'start': match.start(),
                'end': match.end()
            })
    
    # Sort by position in document
    all_matches.sort(key=lambda x: x['start'])
    
    for match in all_matches:
        print(f"  Pattern {match['pattern']}: '{match['text']}' → {match['replacement']}")
    
    print(f"\n📊 Total matches: {len(all_matches)}")

if __name__ == "__main__":
    test_name_recognition()