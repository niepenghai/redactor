#!/usr/bin/env python3
"""
Quick test suite for the PDF Document Redactor - fast version for development.
"""

import os
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.redactor import FinancialDocumentRedactor
from core.enhanced_processor import EnhancedPDFProcessor

def quick_test():
    """Run quick tests on the redactor."""
    print("🚀 Quick Test Suite for PDF Document Redactor")
    print("=" * 60)
    
    # Test file path
    test_file = "../data/input/wells_fargo/wellsfargo.pdf"
    if not os.path.exists(test_file):
        print("❌ Test file not found. Please ensure Wells Fargo PDF exists at:")
        print(f"   {os.path.abspath(test_file)}")
        return
    
    output_dir = tempfile.mkdtemp(prefix="quick_test_")
    print(f"📁 Output directory: {output_dir}")
    
    try:
        # Test 1: Basic functionality
        print("\n📋 Test 1: Basic Processing")
        redactor = FinancialDocumentRedactor()
        redactor.update_config({"replacement_mode": "realistic"})
        
        output_file = os.path.join(output_dir, "quick_test_redacted.pdf")
        success = redactor.redact_pdf(
            input_pdf="wellsfargo.pdf",
            output_pdf="quick_test_redacted.pdf", 
            input_folder=os.path.dirname(os.path.abspath(test_file)),
            output_folder=output_dir
        )
        
        if success and os.path.exists(output_file):
            file_size = os.path.getsize(output_file) // 1024
            print(f"✅ Basic processing successful ({file_size}KB output)")
        else:
            print("❌ Basic processing failed")
            return
        
        # Test 2: Enhanced processing with reporting
        print("\n📋 Test 2: Enhanced Processing with Reporting")
        processor = EnhancedPDFProcessor({
            "replacement_mode": "realistic",
            "enabled_categories": {
                "ssn": True,
                "phone": True,
                "names": True,
                "address": True,
                "email": True
            }
        })
        
        enhanced_output = os.path.join(output_dir, "enhanced_test_redacted.pdf")
        result = processor.process_pdf_with_reporting(os.path.abspath(test_file), enhanced_output)
        
        if result['success']:
            report = result['redaction_report']
            print(f"✅ Enhanced processing successful")
            print(f"   📊 Document type: {report['document_type']}")
            print(f"   🔒 Total redactions: {report['total_redactions']}")
            print(f"   📋 Categories: {list(report['redactions_by_category'].keys())}")
            
            # Show some examples of what was redacted
            if report['detailed_redactions']:
                print(f"\n🔍 Sample redactions:")
                for i, redaction in enumerate(report['detailed_redactions'][:5]):
                    category = redaction['category']
                    original = redaction['original']
                    replacement = redaction['replacement']
                    print(f"   {i+1}. [{category}] '{original}' → '{replacement}'")
            
            # Check for potential issues
            issues = []
            
            # Check for over-redaction (safe words being redacted)
            safe_words = ['Wells Fargo', 'Bank', 'Account', 'Statement', 'Balance', 'Date']
            for redaction in report['detailed_redactions']:
                original = redaction['original'].strip()
                if any(safe_word.lower() in original.lower() for safe_word in safe_words):
                    issues.append(f"Safe word redacted: '{original}'")
            
            if issues:
                print(f"\n⚠️  Potential issues found:")
                for issue in issues[:3]:  # Show first 3
                    print(f"   • {issue}")
            else:
                print(f"\n✅ No obvious over-redaction issues detected")
                
        else:
            print(f"❌ Enhanced processing failed: {result.get('error')}")
            return
        
        # Test 3: Compare different modes
        print("\n📋 Test 3: Mode Comparison")
        modes = ['generic', 'realistic']
        
        for mode in modes:
            processor = EnhancedPDFProcessor({"replacement_mode": mode})
            mode_output = os.path.join(output_dir, f"{mode}_mode_test.pdf")
            result = processor.process_pdf_with_reporting(os.path.abspath(test_file), mode_output)
            
            if result['success']:
                report = result['redaction_report']
                print(f"✅ {mode} mode: {report['total_redactions']} redactions")
                
                # Show first replacement as example
                if report['detailed_redactions']:
                    first = report['detailed_redactions'][0]
                    print(f"   Example: '{first['original']}' → '{first['replacement']}'")
            else:
                print(f"❌ {mode} mode failed")
        
        print(f"\n🎉 Quick tests completed!")
        print(f"📁 Check output files in: {output_dir}")
        print(f"📄 Test files generated:")
        for file in os.listdir(output_dir):
            if file.endswith('.pdf'):
                size = os.path.getsize(os.path.join(output_dir, file)) // 1024
                print(f"   • {file} ({size}KB)")
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()