#!/usr/bin/env python3
"""
Comprehensive test case for PDF redaction verification.
Tests that items that should be redacted are properly redacted,
and items that shouldn't be redacted remain unchanged.
"""

import sys
import os
import tempfile
import fitz  # PyMuPDF

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enhanced_processor import EnhancedPDFProcessor
from core.redactor import FinancialDocumentRedactor


def create_comprehensive_test_pdf():
    """Create a test PDF with various items that should and shouldn't be redacted."""
    
    doc = fitz.open()  # Create new PDF
    page = doc.new_page()  # Add a page
    
    # Test content with items that SHOULD be redacted and items that SHOULD NOT be redacted
    test_content = """
Wells Fargo Bank Statement Test Document

=== ITEMS THAT SHOULD BE REDACTED ===

Names:
- Account Holder: XIA LIN
- Customer: QIZHI CHEN  
- Authorized User: John Smith
- Beneficiary: Sarah Johnson

SSNs:
- SSN: 123-45-6789
- Social Security: 987-65-4321

Phone Numbers:
- Phone: (555) 123-4567
- Contact: 800-555-0199

Account Information:  
- Account: 123456789012
- Routing: 121000248
- Credit Card: 4532-1234-5678-9012

Email Addresses:
- Email: john.doe@example.com
- Contact: customer@test.org

Addresses:
- 123 Main Street, Anytown CA 90210
- 456 Oak Avenue, Springfield IL 62701

=== ITEMS THAT SHOULD NOT BE REDACTED ===

Company Names (Business Context):
- Wells Fargo Bank
- Bank of America
- Chase Manhattan Bank
- Paypal Inst
- Amazon Purchase
- Google Services Inc

Transaction Descriptions:
- Direct Deposit
- ATM Withdrawal  
- Online Transfer
- Bill Pay
- Overdraft Fee

Transaction IDs/References:
- Ref #240112
- Transaction 2642814139
- ID: 117681817

Generic Terms:
- Account Summary
- Routing Number (RTN)
- Available Balance
- Current Balance
- Service Charge

Dates and Amounts:
- January 25, 2024
- $1,234.56
- -$45.99
- +$2,500.00

Address-like but NOT addresses:
- P.O. Box 6995 (return address on statement)
- Portland, OR 97228-6995 (bank address)

General Business Terms:
- Customer Service
- Online Banking
- Mobile Deposit
- Direct Deposit Form
- Statement Period
"""
    
    # Insert text
    page.insert_text((50, 50), test_content, fontsize=10)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
    doc.save(temp_file.name)
    doc.close()
    
    return temp_file.name


def test_comprehensive_redaction():
    """Test comprehensive redaction verification."""
    print("🧪 Testing Comprehensive PDF Redaction Verification")
    print("=" * 60)
    
    # Create test PDF
    test_pdf = create_comprehensive_test_pdf()
    print(f"📄 Created test PDF: {test_pdf}")
    
    try:
        # Read original content
        original_doc = fitz.open(test_pdf)
        original_text = ""
        for page in original_doc:
            original_text += page.get_text()
        original_doc.close()
        
        print(f"📊 Original text length: {len(original_text)} characters")
        
        # Initialize redactor with realistic mode
        redactor = FinancialDocumentRedactor()
        redactor.update_config({"replacement_mode": "realistic"})
        
        # Initialize enhanced processor
        processor = EnhancedPDFProcessor(redactor.config)
        
        print(f"🔧 Configuration: {redactor.config.get('replacement_mode')}")
        enabled_categories = redactor.config.get('enabled_categories', {})
        enabled = [name for name, enabled in enabled_categories.items() if enabled]
        print(f"📋 Enabled categories: {', '.join(enabled)}")
        
        # Process the PDF
        print("\n🔄 Processing PDF...")
        output_dir = tempfile.mkdtemp()
        output_filename = "test_redacted.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        result = processor.process_pdf_with_reporting(test_pdf, output_path)
        
        if result and result.get('success'):
            redaction_report = result.get('redaction_report', {})
            total_redactions = redaction_report.get('total_redactions', 0)
            redactions_by_category = redaction_report.get('redactions_by_category', {})
            
            print(f"✅ Processing completed")
            print(f"📊 Total redactions: {total_redactions}")
            print(f"📁 Output file: {output_path}")
            
            # Show redactions by category
            if redactions_by_category:
                print(f"\n📋 Redactions by category:")
                for category, count in redactions_by_category.items():
                    print(f"  {category}: {count} redactions")
            
            # Read the redacted PDF
            if output_path and os.path.exists(output_path):
                print("\n🔍 Reading redacted PDF content:")
                redacted_doc = fitz.open(output_path)
                redacted_text = ""
                for page in redacted_doc:
                    redacted_text += page.get_text()
                redacted_doc.close()
                
                print(f"📊 Redacted text length: {len(redacted_text)} characters")
                
                # Test items that SHOULD be redacted
                print(f"\n✅ TESTING ITEMS THAT SHOULD BE REDACTED:")
                should_be_redacted = [
                    "XIA LIN",
                    "QIZHI CHEN", 
                    "John Smith",
                    "Sarah Johnson",
                    "123-45-6789",
                    "987-65-4321",
                    "(555) 123-4567",
                    "800-555-0199",
                    "123456789012",
                    "121000248",
                    "4532-1234-5678-9012",
                    "john.doe@example.com",
                    "customer@test.org",
                    "123 Main Street",
                    "456 Oak Avenue"
                ]
                
                redaction_success = 0
                redaction_failures = []
                
                for item in should_be_redacted:
                    if item not in redacted_text:
                        print(f"  ✅ SUCCESS: '{item}' was redacted")
                        redaction_success += 1
                    else:
                        print(f"  ❌ FAILED: '{item}' still found in redacted PDF!")
                        redaction_failures.append(item)
                
                # Test items that SHOULD NOT be redacted
                print(f"\n❌ TESTING ITEMS THAT SHOULD NOT BE REDACTED:")
                should_not_be_redacted = [
                    "Wells Fargo Bank",
                    "Bank of America", 
                    "Chase Manhattan Bank",
                    "Paypal Inst",
                    "Amazon Purchase",
                    "Google Services Inc",
                    "Direct Deposit",
                    "ATM Withdrawal",
                    "Online Transfer",
                    "Bill Pay",
                    "Overdraft Fee",
                    "240112",
                    "2642814139", 
                    "117681817",
                    "Account Summary",
                    "Routing Number (RTN)",
                    "Available Balance",
                    "Current Balance",
                    "Service Charge",
                    "January 25, 2024",
                    "$1,234.56",
                    "-$45.99",
                    "+$2,500.00",
                    "P.O. Box 6995",
                    "Portland, OR 97228-6995",
                    "Customer Service",
                    "Online Banking",
                    "Mobile Deposit"
                ]
                
                preservation_success = 0
                preservation_failures = []
                
                for item in should_not_be_redacted:
                    if item in redacted_text:
                        print(f"  ✅ SUCCESS: '{item}' was preserved (not redacted)")
                        preservation_success += 1
                    else:
                        print(f"  ❌ FAILED: '{item}' was incorrectly redacted!")
                        preservation_failures.append(item)
                
                # Summary
                print(f"\n📊 VERIFICATION SUMMARY:")
                print(f"  Items that should be redacted: {redaction_success}/{len(should_be_redacted)} ✅")
                print(f"  Items that should be preserved: {preservation_success}/{len(should_not_be_redacted)} ✅")
                
                total_tests = len(should_be_redacted) + len(should_not_be_redacted)
                total_success = redaction_success + preservation_success
                success_rate = (total_success / total_tests) * 100 if total_tests > 0 else 0
                
                print(f"  Overall Success Rate: {success_rate:.1f}% ({total_success}/{total_tests})")
                
                if redaction_failures:
                    print(f"\n❌ REDACTION FAILURES (should be redacted but weren't):")
                    for item in redaction_failures:
                        print(f"  - {item}")
                
                if preservation_failures:
                    print(f"\n❌ PRESERVATION FAILURES (shouldn't be redacted but were):")
                    for item in preservation_failures:
                        print(f"  - {item}")
                
                if success_rate == 100:
                    print(f"\n🎉 ALL TESTS PASSED! Perfect redaction verification.")
                elif success_rate >= 90:
                    print(f"\n✅ Most tests passed. Minor issues to address.")
                else:
                    print(f"\n⚠️  Significant issues found. Redaction logic needs improvement.")
                        
            else:
                print("❌ Redacted PDF not found or not created")
        else:
            print("❌ Processing failed")
            if result:
                print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if os.path.exists(test_pdf):
            os.unlink(test_pdf)
        print(f"\n🧹 Cleaned up test file: {test_pdf}")


if __name__ == "__main__":
    test_comprehensive_redaction()