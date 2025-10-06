# 📄 PDF Document Redactor - Usage Guide

A comprehensive tool for redacting sensitive information from financial documents with realistic fake data replacement.

## 🚀 Quick Start

### 1. Installation
```bash
# Install dependencies
pip install PyMuPDF pywebview pyinstaller

# Or install as package
pip install -e .
```

### 2. Run the GUI (Recommended)
```bash
python gui_enhanced.py
```

### 3. Alternative: Command Line
```bash
python main.py
```

## 🎯 Key Features

### ✨ Smart Detection
- **Names (NLP-Powered)**: `XIA LIN`, `QIZHI CHEN`, `John Smith` - Uses advanced spaCy NLP to accurately detect personal names while avoiding false positives like "Wells Fargo" or "Main Street"
- **Addresses**: `2601 CHOCOLATE ST`, `PLEASANTON CA 94588-8436` 
- **Phone Numbers**: `(555) 123-4567`, `800-742-4932`
- **SSN/Tax IDs**: `123-45-6789`, `12-3456789`
- **Account Numbers**: Bank accounts, credit cards, routing numbers
- **Email Addresses**: `user@example.com`

#### 🤖 Advanced Name Recognition
Our NLP-based name detection:
- ✅ **Accurately detects**: International names, titles (Dr. Smith), contextual names
- ❌ **Avoids false positives**: Bank names, street names, business terms, account numbers
- 🌍 **Multi-language support**: Works with various name formats including Asian names

### 🎭 Replacement Modes

#### Realistic Mode (Default)
```
XIA LIN → Michael Johnson
2601 CHOCOLATE ST → 4567 OAK AVE  
(555) 123-4567 → (444) 555-7890
123-45-6789 → 987-65-4321
```

#### Generic Mode
```
XIA LIN → [FULL NAME]
2601 CHOCOLATE ST → [STREET ADDRESS]
(555) 123-4567 → (XXX) XXX-XXXX
123-45-6789 → XXX-XX-XXXX
```

#### Custom Mode
```
XIA LIN → [CLIENT NAME]
2601 CHOCOLATE ST → [ADDRESS REDACTED]
```

## 🖥️ GUI Usage

### Enhanced GUI (`gui_enhanced.py`)
**Best option** - Full-featured interface with detailed reporting.

**Features**:
- 📁 Multi-file selection
- 🎛️ Mode selection with descriptions
- 📊 Real-time processing log
- 🔍 Detailed redaction report
- 📈 Statistical summary
- 💾 Direct file download

**Usage Steps**:
1. Click "📂 Select PDF Files"
2. Choose replacement mode (Realistic recommended)
3. Click "📁 Select Output Folder"
4. Click "🔒 Process X File(s)"
5. Review results in the three tabs:
   - **Processing Log**: Real-time progress
   - **Redaction Details**: What was replaced with what
   - **Summary**: Statistics and overview

## 📊 Understanding Results

### Detailed Report Example
```
📄 FILE: bank_statement.pdf
📋 Document Type: Bank Statement
🔒 Total Redactions: 45

🔍 DETAILED REPLACEMENTS:

 1. [Names] Page 1
    📝 Original:     'XIA LIN'
    🔄 Replaced with: 'Michael Johnson'

 2. [Address] Page 1  
    📝 Original:     '2601 CHOCOLATE ST'
    🔄 Replaced with: '4567 OAK AVE'

 3. [Phone] Page 2
    📝 Original:     '(555) 123-4567'
    🔄 Replaced with: '(444) 555-7890'
```

### Quality Indicators
- ✅ **Good**: Realistic replacements, consistent data
- ⚠️ **Warning**: Some over-redaction of safe terms
- ❌ **Issue**: Text overlapping or layout problems

## 🔧 Configuration

### Editing `config.json`
```json
{
    "replacement_mode": "realistic",
    "enabled_categories": {
        "ssn": true,
        "phone": true,
        "names": true,
        "address": true,
        "email": true,
        "account_number": true
    }
}
```

### Custom Replacement Values
```json
{
    "replacement_mode": "custom",
    "replacement_settings": {
        "custom_replacements": {
            "ssn": "[CONFIDENTIAL-SSN]",
            "names": "[EMPLOYEE-NAME]",
            "address": "[ADDRESS-REDACTED]"
        }
    }
}
```

## 🧪 Testing Your Setup

### Quick Test
```bash
cd tests
python test_quick.py
```

**Expected**: Should detect names like "XIA LIN", "QIZHI CHEN" and addresses.

### NLP Name Detection Test
```bash
cd tests
python test_nlp_names.py
```

**Checks**: Tests NLP-based name recognition accuracy, ensuring no false positives for business names or common terms.

### Full Test Suite
```bash
cd tests  
python test_comprehensive.py
```

**Checks**: Over-redaction, text overlapping, performance, etc.

## 📁 Project Structure

```
redactor/
├── gui_enhanced.py          # Main GUI interface
├── main.py                  # Command line interface
├── core/                    # Core processing engine
│   ├── redactor.py         # Main redaction logic
│   └── pdf_processor.py    # PDF manipulation
├── config/                  # Configuration and patterns
│   ├── patterns.py         # Redaction patterns
│   └── manager.py          # Config management  
├── utils/                   # Utilities
│   └── realistic_generators.py # Realistic data generation
├── tests/                   # Test suite
│   ├── test_quick.py       # Quick development tests
│   ├── test_nlp_names.py   # NLP name recognition tests
│   ├── test_comprehensive.py # Full test suite
│   └── README.md           # Testing documentation
├── data/input/             # Test data (add your PDFs here)
└── .github/workflows/      # Auto-build for Windows/Mac
```

## 🏗️ Building Executables

### Local Build
```bash
# Build for current platform
pyinstaller --onefile --windowed gui_enhanced.py
```

### Cross-Platform (GitHub Actions)
```bash
# Push to GitHub - automatic builds for Windows, Mac, Linux
git tag v1.0.0
git push origin v1.0.0
```

Downloads available in GitHub Releases.

## 🛡️ Security Notes

### ✅ Best Practices
- **Always verify** redacted documents before sharing
- **Test first** with sample documents
- **Review settings** to ensure appropriate redaction level
- **Keep originals secure** and delete when no longer needed

### ⚠️ Limitations
- **Image text**: Cannot redact text embedded in images
- **Complex layouts**: May have issues with very complex PDF layouts
- **False positives**: May occasionally redact non-sensitive information
- **Language support**: Optimized for English documents

## 🔍 Troubleshooting

### Common Issues

**Names not detected**
- Check `"names": true` in config.json
- Verify spaCy is installed: `pip install spacy && python -m spacy download en_core_web_sm`
- International names (like XIA LIN) should be detected automatically
- If NLP detection fails, fallback regex patterns will be used

**Text overlapping after redaction**
- Review output PDFs manually
- May need to adjust redaction method for complex layouts

**Over-redaction (safe words redacted)**
- Our new NLP-based detection significantly reduces false positives
- Run `python tests/test_nlp_names.py` to verify name detection accuracy
- If issues persist, check the detailed redaction report for specific patterns

**Performance issues**
- Process smaller batches of files
- Close other applications to free memory
- Use SSD storage for better I/O performance

### Getting Help

1. **Check test results** with `test_quick.py`
2. **Review detailed logs** in GUI processing tab
3. **Manually inspect** output PDFs
4. **Adjust configuration** based on results

## 📈 Version History

- **v2.0** - Enhanced GUI, realistic data, detailed reporting
- **v1.0** - Basic redaction with generic replacements

## 🎯 Use Cases

### Financial Services
- Redact customer bank statements for training
- Prepare sample documents for demonstrations
- Anonymize documents for testing

### Healthcare  
- Remove patient identifiers from forms
- Create training datasets with fake data

### Legal/Compliance
- Redact sensitive information for discovery
- Prepare documents for public disclosure

### Education/Training
- Create realistic training materials
- Demonstrate document processing workflows