#!/usr/bin/env python3
"""
Test NLP-based name recognition to verify it doesn't over-match common words.
"""

import re
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.patterns import get_nlp_name_patterns, enhance_patterns_with_nlp, get_financial_patterns

def test_nlp_name_detection():
    """Test NLP name detection with examples that should and should not be detected."""
    
    print("🤖 NLP-Based Name Recognition Testing")
    print("=" * 50)
    
    # Test cases - names that SHOULD be detected
    positive_test_cases = [
        "XIA LIN",
        "QIZHI CHEN", 
        "John Smith",
        "Mary Johnson",
        "Dr. Michael Brown",
        "Account Holder: XIA LIN",
        "Customer: QIZHI CHEN",
        "Signature: John Smith",
    ]
    
    # Test cases - words/phrases that should NOT be detected as names
    negative_test_cases = [
        "Main Street",       # Street name
        "Oak Avenue",        # Street name  
        "CA 94588",         # State + ZIP
        "ST AVE",           # Street abbreviations
        "Wells Fargo",      # Bank name
        "Bank of America",  # Bank name
        "Customer Service", # Service department
        "Account Summary",  # Document section
        "Account Balance",  # Balance term
        "Total Available",  # Financial term
        "Current Statement",# Document term
        "Wells Fargo Bank", # Full bank name
        "American Express", # Credit card company
        "Online Banking",   # Service term
        "Direct Deposit",   # Banking term
        "ATM Withdrawal",   # Transaction type
        "Mobile Deposit",   # Service type
        "Overdraft Protection", # Service term
        "Interest Earned",  # Financial term
        "Service Fee",      # Fee type
        "Monthly Fee",      # Fee type
        "Annual Fee",       # Fee type
    ]
    
    print(f"📋 Testing {len(positive_test_cases)} positive cases (should detect names):")
    print()
    
    for test_text in positive_test_cases:
        print(f"Testing: '{test_text}'")
        nlp_patterns = get_nlp_name_patterns(test_text)
        
        if nlp_patterns:
            for pattern, replacement in nlp_patterns:
                # Convert pattern back to readable text
                readable_pattern = pattern.replace('\\b', '').replace('\\', '')
                print(f"  ✅ NLP detected: '{readable_pattern}' → {replacement}")
        else:
            print(f"  ❌ Should have detected name but didn't!")
        print()
    
    print(f"📋 Testing {len(negative_test_cases)} negative cases (should NOT detect as names):")
    print()
    
    false_positives = []
    for test_text in negative_test_cases:
        print(f"Testing: '{test_text}'")
        nlp_patterns = get_nlp_name_patterns(test_text)
        
        if nlp_patterns:
            false_positives.append(test_text)
            for pattern, replacement in nlp_patterns:
                readable_pattern = pattern.replace('\\b', '').replace('\\', '')
                print(f"  ❌ FALSE POSITIVE: '{readable_pattern}' → {replacement}")
        else:
            print(f"  ✅ Correctly ignored (not a name)")
        print()
    
    # Test full document context
    print("📄 Testing in realistic document context:")
    print("-" * 40)
    
    sample_document = """
    Wells Fargo Bank Account Statement
    
    Account Holder: XIA LIN
    Account Number: 1234567890
    Statement Period: January 2024
    
    Customer: QIZHI CHEN
    Address: 2601 CHOCOLATE ST
             PLEASANTON CA 94588-8436
    
    Account Summary for John Smith
    Wells Fargo Bank Customer Service: (800) 742-4932
    
    Recent Transactions:
    01/15  Direct Deposit          +$2,500.00
    01/16  ATM Withdrawal         -$60.00  Main Street
    01/17  Online Purchase        -$45.32  Amazon
    01/18  Mobile Deposit         +$150.00
    01/19  Service Fee            -$12.00  Monthly Fee
    
    Dr. Michael Brown - Account Representative
    For questions, contact Customer Service
    """
    
    print("Sample document extract:")
    print(sample_document[:200] + "...")
    print()
    
    # Get NLP patterns for the full document
    nlp_patterns = get_nlp_name_patterns(sample_document)
    
    print(f"🤖 NLP detected {len(nlp_patterns)} potential names:")
    for i, (pattern, replacement) in enumerate(nlp_patterns, 1):
        readable_pattern = pattern.replace('\\b', '').replace('\\', '')
        print(f"  {i}. '{readable_pattern}' → {replacement}")
    
    # Summary
    print()
    print("📊 SUMMARY:")
    print(f"  • Total test cases: {len(positive_test_cases) + len(negative_test_cases)}")
    print(f"  • Should detect: {len(positive_test_cases)}")
    print(f"  • Should NOT detect: {len(negative_test_cases)}")
    print(f"  • False positives: {len(false_positives)}")
    
    if false_positives:
        print(f"  ❌ False positives found: {', '.join(false_positives)}")
        print("  → Consider refining NLP detection rules")
    else:
        print("  ✅ No false positives detected!")
    
    print(f"  • Document analysis: {len(nlp_patterns)} names detected")

def test_enhanced_patterns_integration():
    """Test the enhanced patterns integration with NLP."""
    
    print("\n" + "=" * 50)
    print("🔗 Testing Enhanced Patterns Integration")
    print("=" * 50)
    
    test_text = "Account Holder: XIA LIN lives at 123 Main Street, Wells Fargo customer John Smith."
    
    # Get base patterns
    base_patterns = get_financial_patterns()
    
    # Enhance with NLP
    enhanced_patterns = enhance_patterns_with_nlp(base_patterns, test_text)
    
    print(f"📝 Test text: {test_text}")
    print()
    print(f"📊 Base name patterns: {len(base_patterns['names'])}")
    print(f"📊 Enhanced name patterns: {len(enhanced_patterns['names'])}")
    
    print("\nEnhanced name patterns:")
    for i, (pattern, replacement) in enumerate(enhanced_patterns['names'], 1):
        if pattern != '__NLP_NAMES__':
            readable_pattern = pattern.replace('\\b', '').replace('\\', '') if pattern.startswith('\\b') else pattern
            print(f"  {i}. {readable_pattern} → {replacement}")

if __name__ == "__main__":
    test_nlp_name_detection()
    test_enhanced_patterns_integration()