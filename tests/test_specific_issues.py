#!/usr/bin/env python3
"""
Test specific issues reported:
1. XIA LIN and QIZHI CHEN not being detected
2. Paypal Inst being incorrectly identified as address
"""

import re
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.patterns import get_financial_patterns, get_nlp_name_patterns, enhance_patterns_with_nlp

def test_specific_name_detection():
    """Test XIA LIN and QIZHI CHEN detection specifically."""
    print("🔍 Testing Specific Name Detection Issues")
    print("=" * 50)
    
    test_cases = [
        "XIA LIN",
        "QIZHI CHEN",
        "Account Holder: XIA LIN", 
        "Customer: QIZHI CHEN",
        "XIA LIN account holder",
        "QIZHI CHEN customer details"
    ]
    
    for test_text in test_cases:
        print(f"Testing: '{test_text}'")
        
        # Test NLP detection
        nlp_patterns = get_nlp_name_patterns(test_text)
        if nlp_patterns:
            for pattern, replacement in nlp_patterns:
                readable = pattern.replace('\\b', '').replace('\\', '')
                print(f"  🤖 NLP: '{readable}' → {replacement}")
        else:
            print("  ❌ NLP: No detection")
        
        # Test enhanced patterns 
        base_patterns = get_financial_patterns()
        enhanced = enhance_patterns_with_nlp(base_patterns, test_text)
        
        name_matches = []
        for pattern, replacement in enhanced['names']:
            if pattern != '__NLP_NAMES__':
                try:
                    if pattern.startswith('\\b'):
                        # Exact match pattern from NLP
                        match_text = pattern.replace('\\b', '').replace('\\', '')
                        if match_text in test_text:
                            name_matches.append((match_text, replacement))
                    else:
                        # Regex pattern
                        matches = re.findall(pattern, test_text, re.IGNORECASE)
                        for match in matches:
                            name_matches.append((match, replacement))
                except Exception as e:
                    continue
        
        if name_matches:
            for match_text, replacement in name_matches:
                print(f"  ✅ Pattern: '{match_text}' → {replacement}")
        else:
            print("  ❌ Pattern: No matches")
        
        print()

def test_address_false_positives():
    """Test address pattern false positives."""
    print("🏠 Testing Address False Positives")
    print("=" * 40)
    
    test_cases = [
        # Should NOT be addresses
        "Paypal Inst",
        "Paypal Institution", 
        "Amazon Inst",
        "Google Inc",
        "Apple Corp",
        "Wells Fargo",
        "Bank of America",
        "240112",          # Should not be phone
        "2642814139",      # Should not be account  
        "117681817",       # Should not be address
        
        # SHOULD be addresses
        "123 Main Street",  
        "456 Oak Avenue",   
    ]
    
    patterns = get_financial_patterns()['address']
    
    for test_text in test_cases:
        print(f"Testing: '{test_text}'")
        
        matched = False
        for pattern, replacement in patterns:
            try:
                match = re.search(pattern, test_text, re.IGNORECASE)
                if match:
                    print(f"  ❌ Address pattern matched: '{match.group()}' → {replacement}")
                    matched = True
            except Exception as e:
                continue
        
        if not matched:
            # Check if it should have matched (real addresses)
            if any(addr_word in test_text.lower() for addr_word in ['street', 'avenue', 'road', 'drive']):
                if any(char.isdigit() for char in test_text):  # Has numbers
                    print(f"  ⚠️  Should have matched but didn't (real address)")
                else:
                    print(f"  ✅ Correctly ignored (no address number)")
            else:
                print(f"  ✅ Correctly ignored (not an address)")
        
        print()

def test_phone_false_positives():
    """Test phone number pattern false positives."""
    print("📞 Testing Phone Number False Positives")
    print("=" * 45)
    
    test_cases = [
        # Should NOT be phone numbers
        "240112",
        "117681817", 
        "2642814139",
        "123456",
        "987654321",
        
        # SHOULD be phone numbers
        "(555) 123-4567",
        "555-123-4567", 
        "5551234567",
        "(800) 742-4932",
    ]
    
    patterns = get_financial_patterns()['phone']
    
    for test_text in test_cases:
        print(f"Testing: '{test_text}'")
        
        matched = False
        for pattern, replacement in patterns:
            try:
                match = re.search(pattern, test_text, re.IGNORECASE)
                if match:
                    print(f"  ❌ Phone pattern matched: '{match.group()}' → {replacement}")
                    matched = True
            except Exception as e:
                continue
        
        if not matched:
            # Check if it should have matched (real phone numbers)
            if any(char in test_text for char in ['(', ')', '-']) or len(test_text) == 10:
                if test_text.replace('(', '').replace(')', '').replace('-', '').replace(' ', '').isdigit():
                    print(f"  ⚠️  Should have matched but didn't (real phone)")
                else:
                    print(f"  ✅ Correctly ignored (not a phone)")
            else:
                print(f"  ✅ Correctly ignored (not a phone)")
        
        print()

def test_account_false_positives():
    """Test account number pattern false positives."""  
    print("🏦 Testing Account Number False Positives")
    print("=" * 45)
    
    test_cases = [
        # Should NOT be account numbers
        "240112",        # Too short
        "117681817",     # Date-like  
        "2642814139",    # Might be legit but questionable
        "123456",        # Too short
        "12345",         # Too short
        
        # SHOULD be account numbers
        "12345678901234",  # 14 digits
        "1234567890123456", # 16 digits
        "123456789012",    # 12 digits
    ]
    
    patterns = get_financial_patterns()['account_number']
    
    for test_text in test_cases:
        print(f"Testing: '{test_text}' (length: {len(test_text)})")
        
        matched = False
        for pattern, replacement in patterns:
            try:
                match = re.search(pattern, test_text, re.IGNORECASE)
                if match:
                    print(f"  ❌ Account pattern matched: '{match.group()}' → {replacement}")
                    matched = True
            except Exception as e:
                continue
        
        if not matched:
            # Check if it should have matched (8-17 digits)
            if test_text.isdigit() and 8 <= len(test_text) <= 17:
                print(f"  ⚠️  Should have matched but didn't (valid length)")
            else:
                print(f"  ✅ Correctly ignored (invalid format/length)")
        
        print()

def test_full_document_context():
    """Test in a realistic document context."""
    print("📄 Testing Full Document Context")
    print("=" * 35)
    
    sample_text = """
    Wells Fargo Bank Statement
    
    Account Holder: XIA LIN
    Customer ID: QIZHI CHEN
    Address: 2601 CHOCOLATE ST
             PLEASANTON CA 94588
    
    Transaction Details:
    01/15  Paypal Inst           -$45.99
    01/16  Amazon Purchase       -$29.99
    01/17  123 Main Street ATM   -$20.00
    01/18  Direct Deposit       +$2500.00
    """
    
    print("Sample text:")
    print(sample_text[:200] + "...")
    print()
    
    # Test name detection
    print("🔍 Name Detection Results:")
    nlp_patterns = get_nlp_name_patterns(sample_text)
    if nlp_patterns:
        for i, (pattern, replacement) in enumerate(nlp_patterns, 1):
            readable = pattern.replace('\\b', '').replace('\\', '')
            print(f"  {i}. '{readable}' → {replacement}")
    else:
        print("  ❌ No names detected!")
    
    print()
    
    # Test address detection
    print("🏠 Address Detection Results:")
    address_patterns = get_financial_patterns()['address']
    address_matches = []
    
    for pattern, replacement in address_patterns:
        matches = re.finditer(pattern, sample_text, re.IGNORECASE)
        for match in matches:
            address_matches.append((match.group(), replacement))
    
    if address_matches:
        for i, (match_text, replacement) in enumerate(address_matches, 1):
            print(f"  {i}. '{match_text}' → {replacement}")
            if "paypal" in match_text.lower():
                print(f"     ❌ FALSE POSITIVE - This should not be an address!")
    else:
        print("  No addresses detected")

if __name__ == "__main__":
    test_specific_name_detection()
    test_address_false_positives()
    test_phone_false_positives()
    test_account_false_positives()
    test_full_document_context()