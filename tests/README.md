# 📋 Testing Documentation

This directory contains comprehensive tests for the PDF Document Redactor system.

## 🧪 Test Files Overview

### 1. `test_quick.py` - Quick Development Tests
**Purpose**: Fast tests for development and basic functionality verification.

**What it tests**:
- ✅ Basic PDF processing functionality
- ✅ Enhanced processing with detailed reporting
- ✅ Different replacement modes (generic vs realistic)
- ✅ Name and address detection (including international names like XIA LIN, QIZHI CHEN)
- ⚠️ Basic over-redaction detection

**Runtime**: ~30 seconds

### 2. `test_comprehensive.py` - Full Test Suite
**Purpose**: Comprehensive testing of all system features and edge cases.

**What it tests**:
- ✅ Basic functionality and error handling
- ✅ Pattern recognition for all sensitive data types
- ✅ Realistic data generation quality
- ✅ Multiple replacement modes comparison
- ✅ Document type detection accuracy
- ✅ Configuration options validation
- ✅ PDF output quality and integrity
- ✅ Edge cases and error handling
- ✅ Over-redaction detection (safe words protection)
- ✅ Text overlapping issues detection
- ✅ Performance benchmarking

**Runtime**: ~5-10 minutes

### 3. `test_patterns.py` - Pattern Recognition Tests
**Purpose**: Focused testing of regular expression patterns and data detection.

**What it tests**:
- ✅ Individual pattern matching
- ✅ Realistic data generation
- ✅ Specific test cases (XIA LIN, QIZHI CHEN, 2601 CHOCOLATE ST)

**Runtime**: ~5 seconds

## 🚀 How to Run Tests

### Prerequisites
```bash
# Ensure PyMuPDF is installed
pip install PyMuPDF

# Ensure you have the test PDF file
# Place Wells Fargo test PDF at: data/input/wells_fargo/wellsfargo.pdf
```

### Running Tests

#### 1. Quick Test (Recommended for development)
```bash
cd tests
python test_quick.py
```

**Expected Output**:
```
🚀 Quick Test Suite for PDF Document Redactor
============================================================
📁 Output directory: /tmp/quick_test_xxxxx

📋 Test 1: Basic Processing
✅ Basic processing successful (XXXXkb output)

📋 Test 2: Enhanced Processing with Reporting
✅ Enhanced processing successful
   📊 Document type: bank_statement
   🔒 Total redactions: XXXX
   📋 Categories: ['ssn', 'phone', 'names', 'address', 'email']

🔍 Sample redactions:
   1. [names] 'XIA LIN' → 'Michael Johnson'
   2. [address] '2601 CHOCOLATE ST' → '4567 OAK AVE'
   3. [phone] '(555) 123-4567' → '(444) 555-7890'
```

#### 2. Pattern Testing
```bash
cd tests
python test_patterns.py
```

#### 3. Comprehensive Testing (Full validation)
```bash
cd tests
python test_comprehensive.py
```

**Note**: Comprehensive tests take longer but provide detailed analysis.

## 📊 Understanding Test Results

### ✅ Success Indicators
- **Basic Processing**: PDF files are generated without errors
- **Pattern Recognition**: Names like "XIA LIN", "QIZHI CHEN" are detected
- **Address Detection**: Addresses like "2601 CHOCOLATE ST" are found
- **Realistic Mode**: Generated replacements look realistic (not placeholders)

### ⚠️ Warning Signs
- **Over-redaction**: Safe words like "Wells Fargo", "Bank" being redacted
- **Text Overlapping**: PDF layout issues after redaction
- **Low Detection Rate**: Fewer than expected sensitive items found

### ❌ Failure Indicators
- **Processing Errors**: PDF generation fails
- **Pattern Failures**: Names/addresses not detected
- **Output Corruption**: Generated PDFs are unreadable

## 🔧 Test Configuration

### Modifying Test Files
To test with different PDF files, update the `test_file` path in each test:

```python
# In test_quick.py or test_comprehensive.py
test_file = "../data/input/your_folder/your_test.pdf"
```

### Custom Pattern Testing
Add your own test cases to `test_patterns.py`:

```python
test_text = """
Your Name
Your Address  
Your Phone: (555) 123-4567
"""
```

## 📁 Test Output

All tests generate output PDFs in temporary directories. Paths are shown in test output:

```
📁 Check output files in: /tmp/quick_test_xxxxx
📄 Test files generated:
   • quick_test_redacted.pdf (XXXkb)
   • enhanced_test_redacted.pdf (XXXkb)
   • generic_mode_test.pdf (XXXkb)
   • realistic_mode_test.pdf (XXXkb)
```

**Manual Verification**: Always manually review generated PDFs to ensure:
1. ✅ Sensitive information is properly redacted
2. ✅ Replacements look realistic and appropriate  
3. ✅ No text overlapping or layout issues
4. ✅ No over-redaction of safe information

## 🐛 Troubleshooting

### Common Issues

**1. "Test file not found"**
```bash
# Ensure test file exists
ls -la ../data/input/wells_fargo/wellsfargo.pdf
```

**2. "PyMuPDF not installed"**
```bash
pip install PyMuPDF
```

**3. "Processing failed"**
- Check PDF file is not corrupted
- Ensure sufficient disk space
- Verify file permissions

**4. "No redactions found"**
- Check if patterns are enabled in config.json
- Verify PDF contains extractable text (not just images)
- Review pattern definitions in config/patterns.py

### Performance Issues

**Tests running too slow?**
- Use `test_quick.py` for development
- Reduce test PDF file size
- Check available system memory

**High memory usage?**
- Process smaller PDF files
- Restart Python interpreter between tests

## 📈 Test Quality Metrics

### Good Test Results
- **Pattern Detection**: >90% of expected sensitive items found
- **Realistic Generation**: <10% placeholder-style replacements
- **Processing Speed**: <10 seconds for typical documents
- **Over-redaction Rate**: <5% of total redactions

### Areas for Improvement
- **Detection Accuracy**: Add more test cases for edge cases
- **Performance**: Profile and optimize slow operations
- **Coverage**: Test with more document types and formats

## 💡 Contributing New Tests

When adding new test cases:

1. **Add specific test data** to verify edge cases
2. **Include expected results** for validation
3. **Test both positive and negative cases**
4. **Document any special requirements**

Example new test:
```python
def test_international_names():
    \"\"\"Test detection of various international name formats.\"\"\"
    test_cases = [
        ("JOSÉ MARÍA", "should detect Spanish names"),
        ("李小明", "should detect Chinese characters"),
        ("محمد احمد", "should detect Arabic names")
    ]
    # ... implementation
```

This ensures comprehensive coverage and helps maintain code quality.