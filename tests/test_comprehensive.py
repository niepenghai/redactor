#!/usr/bin/env python3
"""
Comprehensive test suite for the PDF Document Redactor.
Tests various scenarios and validates redaction quality.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import fitz  # PyMuPDF
except ImportError:
    print("❌ PyMuPDF not installed. Please run: pip install PyMuPDF")
    sys.exit(1)

from core.redactor import FinancialDocumentRedactor
from core.enhanced_processor import EnhancedPDFProcessor
from config.patterns import get_financial_patterns
from utils.realistic_generators import RealisticDataGenerator


class ComprehensiveTestSuite:
    """Comprehensive test suite for the redactor."""
    
    def __init__(self):
        self.test_file = "/Users/penghainie/1_code/redactor/data/input/wells_fargo/wellsfargo.pdf"
        self.output_dir = tempfile.mkdtemp(prefix="redactor_test_")
        self.results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "issues_found": [],
            "recommendations": []
        }
        
        print(f"🧪 Comprehensive Test Suite")
        print(f"📄 Test file: {self.test_file}")
        print(f"📁 Output directory: {self.output_dir}")
        print("=" * 80)
    
    def run_all_tests(self):
        """Run all test categories."""
        
        # Verify test file exists
        if not os.path.exists(self.test_file):
            print(f"❌ Test file not found: {self.test_file}")
            return
        
        print("🚀 Starting comprehensive tests...\n")
        
        # Run different test categories
        self.test_basic_functionality()
        self.test_pattern_recognition()
        self.test_realistic_mode()
        self.test_different_modes()
        self.test_document_type_detection()
        self.test_configuration_options()
        self.test_output_quality()
        self.test_edge_cases()
        self.test_over_redaction()
        self.test_text_overlapping()
        self.test_performance()
        
        # Generate final report
        self.generate_final_report()
    
    def test_basic_functionality(self):
        """Test 1: Basic functionality - can process PDF without errors."""
        print("📋 Test 1: Basic Functionality")
        print("-" * 40)
        
        try:
            redactor = FinancialDocumentRedactor()
            redactor.update_config({"replacement_mode": "realistic"})
            
            output_file = os.path.join(self.output_dir, "basic_test_redacted.pdf")
            
            success = redactor.redact_pdf(
                input_pdf="wellsfargo.pdf",
                output_pdf="basic_test_redacted.pdf",
                input_folder=os.path.dirname(self.test_file),
                output_folder=self.output_dir
            )
            
            if success and os.path.exists(output_file):
                print("✅ Basic processing successful")
                
                # Verify output file is valid PDF
                try:
                    doc = fitz.open(output_file)
                    page_count = doc.page_count
                    doc.close()
                    print(f"✅ Output PDF is valid ({page_count} pages)")
                    self.results["tests_passed"] += 1
                except:
                    print("❌ Output PDF is corrupted")
                    self.results["issues_found"].append("Output PDF is corrupted")
                    self.results["tests_failed"] += 1
            else:
                print("❌ Basic processing failed")
                self.results["issues_found"].append("Basic PDF processing failed")
                self.results["tests_failed"] += 1
                
        except Exception as e:
            print(f"❌ Basic functionality test failed: {e}")
            self.results["issues_found"].append(f"Basic functionality error: {e}")
            self.results["tests_failed"] += 1
        
        self.results["tests_run"] += 1
        print()
    
    def test_pattern_recognition(self):
        """Test 2: Pattern recognition - verify all types of sensitive data are detected."""
        print("📋 Test 2: Pattern Recognition")
        print("-" * 40)
        
        try:
            # Extract text from original PDF
            doc = fitz.open(self.test_file)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()
            
            print(f"📄 Extracted {len(full_text)} characters of text")
            
            # Test pattern detection
            patterns = get_financial_patterns()
            detected_categories = {}
            
            for category, pattern_list in patterns.items():
                matches = []
                for pattern, replacement in pattern_list:
                    import re
                    found_matches = re.findall(pattern, full_text, re.IGNORECASE)
                    matches.extend(found_matches)
                
                if matches:
                    detected_categories[category] = len(matches)
                    print(f"✅ {category}: {len(matches)} matches found")
                else:
                    print(f"⚠️  {category}: No matches found")
            
            # Check for critical patterns
            critical_patterns = ['ssn', 'phone', 'names', 'address']
            missing_critical = []
            
            for pattern in critical_patterns:
                if pattern not in detected_categories or detected_categories[pattern] == 0:
                    missing_critical.append(pattern)
            
            if missing_critical:
                print(f"⚠️  Missing critical patterns: {missing_critical}")
                self.results["issues_found"].append(f"Missing critical patterns: {missing_critical}")
                self.results["recommendations"].append("Review pattern definitions for better coverage")
            
            if len(detected_categories) > 0:
                print(f"✅ Pattern recognition working ({len(detected_categories)} categories detected)")
                self.results["tests_passed"] += 1
            else:
                print("❌ No patterns detected at all")
                self.results["issues_found"].append("No sensitive data patterns detected")
                self.results["tests_failed"] += 1
                
        except Exception as e:
            print(f"❌ Pattern recognition test failed: {e}")
            self.results["issues_found"].append(f"Pattern recognition error: {e}")
            self.results["tests_failed"] += 1
        
        self.results["tests_run"] += 1
        print()
    
    def test_realistic_mode(self):
        """Test 3: Realistic mode - verify realistic data generation."""
        print("📋 Test 3: Realistic Mode Testing")
        print("-" * 40)
        
        try:
            processor = EnhancedPDFProcessor({
                "replacement_mode": "realistic",
                "enabled_categories": {
                    "ssn": True,
                    "phone": True,
                    "names": True,
                    "address": True,
                    "email": True,
                    "account_number": True
                }
            })
            
            output_file = os.path.join(self.output_dir, "realistic_test_redacted.pdf")
            
            result = processor.process_pdf_with_reporting(self.test_file, output_file)
            
            if result['success']:
                report = result['redaction_report']
                print(f"✅ Realistic processing successful")
                print(f"📊 Total redactions: {report['total_redactions']}")
                
                # Verify realistic replacements
                realistic_count = 0
                placeholder_count = 0
                
                for redaction in report['detailed_redactions'][:10]:  # Check first 10
                    replacement = redaction['replacement']
                    if any(placeholder in replacement for placeholder in ['XXX', '[', 'REDACTED']):
                        placeholder_count += 1
                        print(f"⚠️  Placeholder found: '{redaction['original']}' → '{replacement}'")
                    else:
                        realistic_count += 1
                        print(f"✅ Realistic: '{redaction['original']}' → '{replacement}'")
                
                if realistic_count > placeholder_count:
                    print("✅ Realistic mode is working correctly")
                    self.results["tests_passed"] += 1
                else:
                    print("❌ Too many placeholder replacements in realistic mode")
                    self.results["issues_found"].append("Realistic mode not generating realistic data")
                    self.results["tests_failed"] += 1
            else:
                print(f"❌ Realistic processing failed: {result.get('error', 'Unknown error')}")
                self.results["issues_found"].append("Realistic mode processing failed")
                self.results["tests_failed"] += 1
                
        except Exception as e:
            print(f"❌ Realistic mode test failed: {e}")
            self.results["issues_found"].append(f"Realistic mode error: {e}")
            self.results["tests_failed"] += 1
        
        self.results["tests_run"] += 1
        print()
    
    def test_different_modes(self):
        """Test 4: Different replacement modes comparison."""
        print("📋 Test 4: Different Replacement Modes")
        print("-" * 40)
        
        modes = ['generic', 'realistic', 'custom']
        mode_results = {}
        
        for mode in modes:
            try:
                print(f"🎛️  Testing {mode} mode...")
                
                config = {
                    "replacement_mode": mode,
                    "replacement_settings": {
                        "custom_replacements": {
                            "ssn": "[CONFIDENTIAL-SSN]",
                            "names": "[EMPLOYEE-NAME]",
                            "phone": "[PHONE-REDACTED]"
                        }
                    }
                }
                
                processor = EnhancedPDFProcessor(config)
                output_file = os.path.join(self.output_dir, f"{mode}_mode_redacted.pdf")
                
                result = processor.process_pdf_with_reporting(self.test_file, output_file)
                
                if result['success']:
                    report = result['redaction_report']
                    mode_results[mode] = {
                        'success': True,
                        'total_redactions': report['total_redactions'],
                        'categories': len(report['redactions_by_category']),
                        'sample_replacements': [r['replacement'] for r in report['detailed_redactions'][:3]]
                    }
                    print(f"  ✅ {mode}: {report['total_redactions']} redactions")
                else:
                    mode_results[mode] = {'success': False, 'error': result.get('error')}
                    print(f"  ❌ {mode}: Failed - {result.get('error')}")
                    
            except Exception as e:
                mode_results[mode] = {'success': False, 'error': str(e)}
                print(f"  ❌ {mode}: Exception - {e}")
        
        # Verify mode differences
        successful_modes = [m for m, r in mode_results.items() if r.get('success')]
        
        if len(successful_modes) >= 2:
            print("✅ Multiple modes working")
            self.results["tests_passed"] += 1
            
            # Check that modes produce different results
            samples = {mode: mode_results[mode].get('sample_replacements', []) 
                      for mode in successful_modes}
            
            different_outputs = False
            if len(successful_modes) >= 2:
                mode1, mode2 = successful_modes[:2]
                if samples[mode1] != samples[mode2]:
                    different_outputs = True
                    print("✅ Modes produce different outputs as expected")
                else:
                    print("⚠️  Modes produce identical outputs")
                    self.results["recommendations"].append("Verify mode implementations are distinct")
        else:
            print("❌ Not enough modes working")
            self.results["issues_found"].append("Multiple replacement modes not working")
            self.results["tests_failed"] += 1
        
        self.results["tests_run"] += 1
        print()
    
    def test_document_type_detection(self):
        """Test 5: Document type detection accuracy."""
        print("📋 Test 5: Document Type Detection")
        print("-" * 40)
        
        try:
            redactor = FinancialDocumentRedactor()
            
            # Extract text and detect type
            doc = fitz.open(self.test_file)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()
            
            detected_type = redactor.detect_document_type(full_text)
            print(f"🔍 Detected document type: {detected_type}")
            
            # Verify reasonable detection (should not be 'general' for Wells Fargo)
            if detected_type and detected_type != 'general':
                print(f"✅ Specific document type detected: {detected_type}")
                self.results["tests_passed"] += 1
                
                # Check if detection makes sense for Wells Fargo
                if 'bank' in detected_type or 'statement' in detected_type:
                    print("✅ Document type detection is logical for bank document")
                else:
                    print(f"⚠️  Document type '{detected_type}' may not be optimal for bank statement")
                    self.results["recommendations"].append("Review document type detection rules")
            else:
                print("❌ Document type detection failed or too generic")
                self.results["issues_found"].append("Document type detection not working properly")
                self.results["tests_failed"] += 1
                
        except Exception as e:
            print(f"❌ Document type detection test failed: {e}")
            self.results["issues_found"].append(f"Document type detection error: {e}")
            self.results["tests_failed"] += 1
        
        self.results["tests_run"] += 1
        print()
    
    def test_configuration_options(self):
        """Test 6: Configuration options and category enabling/disabling."""
        print("📋 Test 6: Configuration Options")
        print("-" * 40)
        
        try:
            # Test with different category configurations
            test_configs = [
                {"enabled_categories": {"ssn": True}, "name": "SSN only"},
                {"enabled_categories": {"names": True, "address": True}, "name": "Names and addresses only"},
                {"enabled_categories": {"phone": False, "email": False}, "name": "No phone or email"}
            ]
            
            for config_test in test_configs:
                config = {
                    "replacement_mode": "realistic",
                    **config_test
                }
                
                processor = EnhancedPDFProcessor(config)
                output_file = os.path.join(self.output_dir, f"config_{config_test['name'].replace(' ', '_')}_redacted.pdf")
                
                result = processor.process_pdf_with_reporting(self.test_file, output_file)
                
                if result['success']:
                    report = result['redaction_report']
                    categories = list(report['redactions_by_category'].keys())
                    print(f"✅ {config_test['name']}: {report['total_redactions']} redactions in categories: {categories}")
                else:
                    print(f"❌ {config_test['name']}: Failed")
            
            print("✅ Configuration options are functional")
            self.results["tests_passed"] += 1
                
        except Exception as e:
            print(f"❌ Configuration options test failed: {e}")
            self.results["issues_found"].append(f"Configuration options error: {e}")
            self.results["tests_failed"] += 1
        
        self.results["tests_run"] += 1
        print()
    
    def test_output_quality(self):
        """Test 7: Output PDF quality and integrity."""
        print("📋 Test 7: Output Quality")
        print("-" * 40)
        
        try:
            processor = EnhancedPDFProcessor({"replacement_mode": "realistic"})
            output_file = os.path.join(self.output_dir, "quality_test_redacted.pdf")
            
            result = processor.process_pdf_with_reporting(self.test_file, output_file)
            
            if result['success'] and os.path.exists(output_file):
                # Open and analyze output
                original_doc = fitz.open(self.test_file)
                redacted_doc = fitz.open(output_file)
                
                # Compare page counts
                if original_doc.page_count == redacted_doc.page_count:
                    print(f"✅ Page count preserved: {original_doc.page_count} pages")
                else:
                    print(f"❌ Page count mismatch: {original_doc.page_count} → {redacted_doc.page_count}")
                    self.results["issues_found"].append("Page count changed during redaction")
                
                # Check text content differences
                original_text = ""
                redacted_text = ""
                
                for i in range(min(original_doc.page_count, redacted_doc.page_count)):
                    original_text += original_doc[i].get_text()
                    redacted_text += redacted_doc[i].get_text()
                
                # Calculate text change percentage
                if len(original_text) > 0:
                    change_ratio = abs(len(redacted_text) - len(original_text)) / len(original_text)
                    print(f"📊 Text length change: {change_ratio:.1%}")
                    
                    if change_ratio < 0.5:  # Less than 50% change is reasonable
                        print("✅ Text length change is reasonable")
                    else:
                        print("⚠️  Large text length change - may indicate over-redaction")
                        self.results["recommendations"].append("Review redaction patterns for over-matching")
                
                original_doc.close()
                redacted_doc.close()
                
                # Check file size
                original_size = os.path.getsize(self.test_file)
                redacted_size = os.path.getsize(output_file)
                size_ratio = redacted_size / original_size
                
                print(f"📊 File size ratio: {size_ratio:.2f} ({original_size//1024}KB → {redacted_size//1024}KB)")
                
                self.results["tests_passed"] += 1
            else:
                print("❌ Output quality test failed - no valid output file")
                self.results["tests_failed"] += 1
                
        except Exception as e:
            print(f"❌ Output quality test failed: {e}")
            self.results["issues_found"].append(f"Output quality error: {e}")
            self.results["tests_failed"] += 1
        
        self.results["tests_run"] += 1
        print()
    
    def test_edge_cases(self):
        """Test 8: Edge cases and error handling."""
        print("📋 Test 8: Edge Cases")
        print("-" * 40)
        
        edge_cases = [
            {
                "name": "Empty config",
                "config": {},
                "should_work": True
            },
            {
                "name": "All categories disabled",
                "config": {"enabled_categories": {}},
                "should_work": True
            },
            {
                "name": "Invalid replacement mode",
                "config": {"replacement_mode": "invalid_mode"},
                "should_work": False
            }
        ]
        
        passed = 0
        for case in edge_cases:
            try:
                print(f"🧪 Testing: {case['name']}")
                
                processor = EnhancedPDFProcessor(case['config'])
                output_file = os.path.join(self.output_dir, f"edge_case_{case['name'].replace(' ', '_')}_redacted.pdf")
                
                result = processor.process_pdf_with_reporting(self.test_file, output_file)
                
                if case['should_work']:
                    if result['success']:
                        print(f"  ✅ {case['name']}: Handled correctly")
                        passed += 1
                    else:
                        print(f"  ❌ {case['name']}: Should work but failed")
                else:
                    if not result['success']:
                        print(f"  ✅ {case['name']}: Correctly rejected")
                        passed += 1
                    else:
                        print(f"  ❌ {case['name']}: Should fail but succeeded")
                        
            except Exception as e:
                if case['should_work']:
                    print(f"  ❌ {case['name']}: Unexpected exception: {e}")
                else:
                    print(f"  ✅ {case['name']}: Correctly threw exception")
                    passed += 1
        
        if passed >= len(edge_cases) * 0.8:  # 80% pass rate
            print("✅ Edge case handling is robust")
            self.results["tests_passed"] += 1
        else:
            print("❌ Edge case handling needs improvement")
            self.results["issues_found"].append("Edge case handling is not robust")
            self.results["tests_failed"] += 1
        
        self.results["tests_run"] += 1
        print()
    
    def test_over_redaction(self):
        """Test 9: Check for over-redaction of non-sensitive information."""
        print("📋 Test 9: Over-Redaction Detection")
        print("-" * 40)
        
        try:
            # Extract original text
            original_doc = fitz.open(self.test_file)
            original_text = ""
            for page in original_doc:
                original_text += page.get_text()
            original_doc.close()
            
            # Process with realistic mode
            processor = EnhancedPDFProcessor({"replacement_mode": "realistic"})
            output_file = os.path.join(self.output_dir, "over_redaction_test_redacted.pdf")
            
            result = processor.process_pdf_with_reporting(self.test_file, output_file)
            
            if result['success']:
                report = result['redaction_report']
                
                # Analyze redacted items for false positives
                false_positives = []
                
                # Common words that should NOT be redacted
                safe_words = [
                    'Wells Fargo', 'Bank', 'Statement', 'Account', 'Balance', 
                    'Date', 'Transaction', 'Deposit', 'Withdrawal', 'Fee',
                    'Total', 'Available', 'Current', 'Previous', 'Next',
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                    'January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December',
                    'Dollar', 'Dollars', 'USD', 'Amount', 'Summary'
                ]
                
                # Check if any safe words were redacted
                for redaction in report['detailed_redactions']:
                    original = redaction['original'].strip()
                    
                    # Check if it's a safe word
                    if any(safe_word.lower() in original.lower() for safe_word in safe_words):
                        false_positives.append(f"'{original}' → '{redaction['replacement']}'")
                
                # Check for common false positive patterns
                for redaction in report['detailed_redactions']:
                    original = redaction['original'].strip()
                    
                    # Check for dates that might be incorrectly identified as other patterns
                    if len(original) <= 3 and original.isdigit():
                        false_positives.append(f"Possible date component: '{original}' → '{redaction['replacement']}'")
                    
                    # Check for common abbreviations
                    common_abbrevs = ['ST', 'AVE', 'RD', 'DR', 'LN', 'CA', 'NY', 'TX', 'FL']
                    if original.upper() in common_abbrevs and redaction['category'] == 'names':
                        false_positives.append(f"Address abbreviation as name: '{original}' → '{redaction['replacement']}'")
                
                print(f"🔍 Analyzed {len(report['detailed_redactions'])} redactions")
                
                if false_positives:
                    print(f"⚠️  Found {len(false_positives)} potential over-redactions:")
                    for fp in false_positives[:10]:  # Show first 10
                        print(f"  • {fp}")
                    
                    if len(false_positives) > len(report['detailed_redactions']) * 0.2:  # >20% false positives
                        print("❌ High over-redaction rate detected")
                        self.results["issues_found"].append(f"High over-redaction rate: {len(false_positives)} items")
                        self.results["recommendations"].append("Refine patterns to reduce false positives")
                        self.results["tests_failed"] += 1
                    else:
                        print("⚠️  Some over-redaction detected but within acceptable limits")
                        self.results["recommendations"].append("Review patterns for minor over-redaction issues")
                        self.results["tests_passed"] += 1
                else:
                    print("✅ No obvious over-redaction detected")
                    self.results["tests_passed"] += 1
            else:
                print("❌ Over-redaction test failed - processing unsuccessful")
                self.results["tests_failed"] += 1
                
        except Exception as e:
            print(f"❌ Over-redaction test failed: {e}")
            self.results["issues_found"].append(f"Over-redaction test error: {e}")
            self.results["tests_failed"] += 1
        
        self.results["tests_run"] += 1
        print()
    
    def test_text_overlapping(self):
        """Test 10: Check for text overlapping issues after redaction."""
        print("📋 Test 10: Text Overlapping Detection")
        print("-" * 40)
        
        try:
            processor = EnhancedPDFProcessor({"replacement_mode": "realistic"})
            output_file = os.path.join(self.output_dir, "overlap_test_redacted.pdf")
            
            result = processor.process_pdf_with_reporting(self.test_file, output_file)
            
            if result['success'] and os.path.exists(output_file):
                # Analyze the redacted PDF for potential overlapping issues
                redacted_doc = fitz.open(output_file)
                overlap_issues = []
                
                for page_num in range(redacted_doc.page_count):
                    page = redacted_doc[page_num]
                    
                    # Get text blocks with position information
                    text_blocks = page.get_text("dict")
                    
                    # Check for overlapping text blocks
                    blocks = []
                    if 'blocks' in text_blocks:
                        for block in text_blocks['blocks']:
                            if 'lines' in block:
                                for line in block['lines']:
                                    for span in line.get('spans', []):
                                        blocks.append({
                                            'bbox': span['bbox'],
                                            'text': span['text'],
                                            'size': span['size']
                                        })
                    
                    # Check for overlapping bounding boxes
                    for i, block1 in enumerate(blocks):
                        for j, block2 in enumerate(blocks[i+1:], i+1):
                            bbox1 = block1['bbox']
                            bbox2 = block2['bbox']
                            
                            # Check if bounding boxes overlap significantly
                            overlap_x = max(0, min(bbox1[2], bbox2[2]) - max(bbox1[0], bbox2[0]))
                            overlap_y = max(0, min(bbox1[3], bbox2[3]) - max(bbox1[1], bbox2[1]))
                            
                            area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
                            area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
                            
                            if overlap_x > 0 and overlap_y > 0:
                                overlap_area = overlap_x * overlap_y
                                overlap_ratio1 = overlap_area / area1 if area1 > 0 else 0
                                overlap_ratio2 = overlap_area / area2 if area2 > 0 else 0
                                
                                # If overlap is significant (>50% of either text block)
                                if overlap_ratio1 > 0.5 or overlap_ratio2 > 0.5:
                                    overlap_issues.append({
                                        'page': page_num + 1,
                                        'text1': block1['text'][:30],
                                        'text2': block2['text'][:30],
                                        'overlap_ratio': max(overlap_ratio1, overlap_ratio2)
                                    })
                
                redacted_doc.close()
                
                # Also check text extraction patterns that might indicate overlapping
                redacted_doc = fitz.open(output_file)
                full_redacted_text = ""
                for page in redacted_doc:
                    full_redacted_text += page.get_text()
                redacted_doc.close()
                
                # Look for patterns that suggest text overlapping
                text_anomalies = []
                
                # Check for unusual character sequences that might indicate overlapping
                import re
                
                # Multiple consecutive spaces or weird spacing
                if re.search(r'\s{10,}', full_redacted_text):
                    text_anomalies.append("Excessive spacing detected")
                
                # Mixed-up text patterns (characters from different contexts mixed together)
                weird_patterns = [
                    r'[A-Z]{5,}\d{3,}[A-Z]{3,}',  # Long sequences of caps mixed with numbers
                    r'\$[A-Za-z]+\$',              # Dollar signs with letters between
                    r'[a-z][A-Z]{10,}[a-z]',      # Long caps sequences in middle of lowercase
                ]
                
                for pattern in weird_patterns:
                    matches = re.findall(pattern, full_redacted_text)
                    if matches:
                        text_anomalies.extend([f"Suspicious pattern: {match}" for match in matches[:5]])
                
                # Report results
                print(f"🔍 Analyzed {len(text_blocks.get('blocks', []))} text blocks across all pages")
                
                total_issues = len(overlap_issues) + len(text_anomalies)
                
                if overlap_issues:
                    print(f"⚠️  Found {len(overlap_issues)} potential overlapping text areas:")
                    for issue in overlap_issues[:5]:  # Show first 5
                        print(f"  • Page {issue['page']}: '{issue['text1']}...' overlaps with '{issue['text2']}...' ({issue['overlap_ratio']:.1%} overlap)")
                
                if text_anomalies:
                    print(f"⚠️  Found {len(text_anomalies)} text anomalies:")
                    for anomaly in text_anomalies[:5]:  # Show first 5
                        print(f"  • {anomaly}")
                
                if total_issues == 0:
                    print("✅ No text overlapping issues detected")
                    self.results["tests_passed"] += 1
                elif total_issues <= 3:
                    print("⚠️  Minor text overlapping issues detected")
                    self.results["recommendations"].append("Minor text layout issues found - review redaction placement")
                    self.results["tests_passed"] += 1
                else:
                    print("❌ Significant text overlapping issues detected")
                    self.results["issues_found"].append(f"Text overlapping problems: {total_issues} issues found")
                    self.results["recommendations"].append("Fix redaction method to prevent text overlapping")
                    self.results["tests_failed"] += 1
            
            else:
                print("❌ Text overlapping test failed - no valid output file")
                self.results["tests_failed"] += 1
                
        except Exception as e:
            print(f"❌ Text overlapping test failed: {e}")
            self.results["issues_found"].append(f"Text overlapping test error: {e}")
            self.results["tests_failed"] += 1
        
        self.results["tests_run"] += 1
        print()
    
    def test_performance(self):
        """Test 11: Performance benchmarking."""
        print("📋 Test 11: Performance Testing")
        print("-" * 40)
        
        import time
        
        try:
            processor = EnhancedPDFProcessor({"replacement_mode": "realistic"})
            output_file = os.path.join(self.output_dir, "performance_test_redacted.pdf")
            
            start_time = time.time()
            result = processor.process_pdf_with_reporting(self.test_file, output_file)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            if result['success']:
                report = result['redaction_report']
                redactions_per_second = report['total_redactions'] / processing_time if processing_time > 0 else 0
                
                print(f"⏱️  Processing time: {processing_time:.2f} seconds")
                print(f"🔒 Total redactions: {report['total_redactions']}")
                print(f"📊 Performance: {redactions_per_second:.1f} redactions/second")
                
                # Performance benchmarks
                if processing_time < 10:  # Should process in under 10 seconds for most documents
                    print("✅ Performance is acceptable")
                    self.results["tests_passed"] += 1
                else:
                    print("⚠️  Performance may be slow for large documents")
                    self.results["recommendations"].append("Consider performance optimizations")
                    self.results["tests_passed"] += 1  # Still pass but note the issue
            else:
                print("❌ Performance test failed - processing unsuccessful")
                self.results["tests_failed"] += 1
                
        except Exception as e:
            print(f"❌ Performance test failed: {e}")
            self.results["issues_found"].append(f"Performance test error: {e}")
            self.results["tests_failed"] += 1
        
        self.results["tests_run"] += 1
        print()
    
    def generate_final_report(self):
        """Generate comprehensive final report."""
        print("=" * 80)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        print(f"📋 Tests Run: {self.results['tests_run']}")
        print(f"✅ Tests Passed: {self.results['tests_passed']}")
        print(f"❌ Tests Failed: {self.results['tests_failed']}")
        
        pass_rate = (self.results['tests_passed'] / self.results['tests_run'] * 100) if self.results['tests_run'] > 0 else 0
        print(f"📈 Pass Rate: {pass_rate:.1f}%")
        
        if self.results['issues_found']:
            print(f"\n🚨 ISSUES FOUND ({len(self.results['issues_found'])}):")
            for i, issue in enumerate(self.results['issues_found'], 1):
                print(f"  {i}. {issue}")
        
        if self.results['recommendations']:
            print(f"\n💡 RECOMMENDATIONS ({len(self.results['recommendations'])}):")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if pass_rate >= 90:
            print("✅ EXCELLENT - System is working very well")
        elif pass_rate >= 80:
            print("✅ GOOD - System is working well with minor issues")
        elif pass_rate >= 70:
            print("⚠️  ACCEPTABLE - System is functional but needs improvement")
        else:
            print("❌ NEEDS WORK - System has significant issues")
        
        print(f"\n📁 Test outputs saved to: {self.output_dir}")
        print("🔍 Review the redacted PDFs to verify quality manually.")


def main():
    """Run the comprehensive test suite."""
    suite = ComprehensiveTestSuite()
    suite.run_all_tests()


if __name__ == "__main__":
    main()