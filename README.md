# Financial Document Redactor

A powerful Python library and CLI tool for automatically redacting sensitive information from financial documents including bank statements, W2 forms, tax returns, and pay stubs.

## Features

- **🤖 Automatic Document Detection**: Intelligently identifies document types (bank statements, W2, tax returns, pay stubs)
- **🔒 Comprehensive Redaction**: Redacts SSNs, account numbers, phone numbers, addresses, names, and more
- **🎛️ Multiple Replacement Modes**: Generic placeholders, realistic fake data, or custom replacements
- **👤 NLP-Powered Name Recognition**: Advanced spaCy NLP for accurate personal name detection while avoiding false positives (Wells Fargo, Main Street, etc.)
- **⚙️ Configurable Settings**: Customize what gets redacted through `config.json`
- **📁 Batch Processing**: Process multiple PDF files at once
- **🛡️ Error Handling**: Robust error handling with clear feedback
- **📊 Progress Tracking**: Visual indicators and processing summaries
- **🔌 Library & CLI**: Use as a standalone tool or integrate as a Python library
- **🏗️ Modular Architecture**: Clean separation between core logic and user interface

## Installation

### Prerequisites
- Python 3.7 or higher

### Option 1: Package Installation (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd redactor

# Install as editable package with dependencies
pip install -e .

# Or install with development dependencies
pip install -e .[dev]
```

### Option 2: Direct Dependencies
```bash
# Install required dependencies manually
pip install PyMuPDF>=1.20.0 spacy
python -m spacy download en_core_web_sm
```

### Option 3: Development Setup
```bash
# Clone and set up for development
git clone <repository-url>
cd redactor
pip install -e .[dev]

# Run tests
pytest

# Format code
black .
```

## 🚀 Quick Start

**New to the tool? Check out our [Quick Start Guide](docs/quick-start.md) for a 5-minute setup!**

### 🖥️ GUI Interface (Recommended)
```bash
# Install dependencies
pip install PyMuPDF spacy
python -m spacy download en_core_web_sm

# Launch GUI
python redactor-gui.py
```

### 📋 Command Line Interface  
```bash
# Process a single PDF
python redactor-cli.py document.pdf

# Process multiple files
python redactor-cli.py folder/*.pdf
```

## 📚 Documentation

- **[🚀 Quick Start Guide](docs/quick-start.md)** - Get up and running in 5 minutes
- **[📖 User Guide](docs/user-guide.md)** - Complete usage documentation  
- **[📋 Project Summary](docs/project-summary.md)** - Technical overview and features

3. **Interactive experience**:
   - Enhanced CLI with input validation
   - **NEW**: Replacement mode selection (Generic/Realistic/Custom)
   - Processing previews and confirmations
   - Automatic folder detection and PDF counting
   - Custom pattern template generation
   - Results summary with file size information

### Library Usage (Python Integration)

```python
# Import the main class
from core.redactor import FinancialDocumentRedactor

# Initialize the redactor
redactor = FinancialDocumentRedactor()

# Set replacement mode
redactor.update_config({"replacement_mode": "realistic"})

# Process a single PDF file
success = redactor.redact_pdf(
    input_pdf="bank_statement.pdf",
    output_pdf="bank_statement_redacted.pdf", 
    input_folder="/path/to/input",
    output_folder="/path/to/output"
)

# Process an entire folder
results = redactor.process_folder("/path/to/input", "/path/to/output")
print(f"Processed {results['processed']} files successfully")

# Use with custom patterns
user_patterns = [("ACME Bank", "[BANK NAME]")]
results = redactor.process_folder("/input", "/output", user_patterns)

# Advanced usage with custom config
redactor = FinancialDocumentRedactor("/custom/config.json")
```

## Document Types Supported

| Document Type | Auto-Detection | Redacted Information |
|---------------|----------------|---------------------|
| **Bank Statements** | ✅ | Account numbers, routing numbers, SSN, currency amounts, addresses, names |
| **W2 Forms** | ✅ | SSN, Tax ID/EIN, employer info, currency amounts, addresses, names |
| **Tax Returns** | ✅ | SSN, Tax ID/EIN, currency amounts, addresses, names |
| **Pay Stubs** | ✅ | SSN, employer info, currency amounts, addresses, names |
| **General** | ✅ | All available patterns |

## 🎛️ Replacement Modes

Choose how sensitive information is replaced:

### Generic Mode (Default)
Safe placeholder values for compliance:
- **Social Security Numbers**: `123-45-6789` → `XXX-XX-XXXX`
- **Phone Numbers**: `(555) 123-4567` → `(XXX) XXX-XXXX`
- **Names**: `John Smith` → `[NAME]`
- **Email Addresses**: `user@example.com` → `user@domain.com`

### Realistic Mode  
Fake but plausible data that maintains document readability:
- **Social Security Numbers**: `123-45-6789` → `987-65-4321`
- **Phone Numbers**: `(555) 123-4567` → `(444) 555-6789`
- **Names**: `John Smith` → `Michael Johnson`
- **Email Addresses**: `user@example.com` → `john.doe@example.com`

### Custom Mode
Organization-specific replacements:
- **Social Security Numbers**: `123-45-6789` → `[SSN REDACTED PER POLICY]`
- **Phone Numbers**: `(555) 123-4567` → `[PHONE REDACTED]`
- **Names**: `John Smith` → `[CLIENT NAME]`

## 👤 Personal Name Redaction

Advanced name detection patterns:

- **Full Names**: `John Smith`, `Mary Elizabeth Johnson`
- **Names with Titles**: `Dr. Michael Brown`, `Ms. Sarah Williams` 
- **Middle Initials**: `Jane A. Thompson`, `Robert B. Miller`
- **Context-aware**: 
  - `Account Holder: David Miller` → `Account Holder: [NAME]`
  - `Signature: Jennifer Davis` → `Signature: [NAME]`
  - `Customer: Robert Martinez` → `Customer: [NAME]`

## Redaction Patterns

The tool automatically redacts:

- **Social Security Numbers**: Multiple formats with secure replacement
- **Phone Numbers**: Various formats including international
- **Bank Account Numbers**: 8-17 digit account numbers
- **Routing Numbers**: 9-digit routing numbers with context detection
- **Credit Card Numbers**: Visa, Mastercard, Amex formats
- **Tax ID/EIN**: Employer identification numbers
- **Currency Amounts**: Dollar amounts in various formats
- **Email Addresses**: Complete email address patterns
- **Physical Addresses**: Street addresses and city/state/zip
- **Employer Information**: Company names and employer references
- **Personal Names**: Full names, titles, signatures, and account holders

## Configuration

### config.json

The tool creates a `config.json` file for customization:

```json
{
    "redaction_level": "standard",
    "replacement_mode": "generic",
    "enabled_categories": {
        "ssn": true,
        "phone": true,
        "account_number": true,
        "routing_number": true,
        "credit_card": true,
        "tax_id": true,
        "currency": false,
        "dates": false,
        "email": true,
        "address": true,
        "employer": false,
        "names": true
    },
    "replacement_settings": {
        "use_consistent_replacements": true,
        "realistic_names": ["John Smith", "Jane Doe", "Michael Johnson"],
        "realistic_companies": ["ACME Corp", "Global Industries"],
        "realistic_first_names_male": ["John", "Michael", "David"],
        "realistic_first_names_female": ["Mary", "Patricia", "Jennifer"],
        "realistic_last_names": ["Smith", "Johnson", "Williams"],
        "phone_area_codes": ["555", "444", "333"],
        "email_domains": ["example.com", "test.org", "sample.net"],
        "custom_replacements": {
            "ssn": "[SSN-REDACTED]",
            "names": "[CLIENT NAME]",
            "phone": "[PHONE-REDACTED]"
        }
    },
    "custom_patterns": []
}
```

### Setting Replacement Modes

#### Via CLI
The interactive CLI now prompts for replacement mode:
```
🎛️  Replacement Mode Selection
--------------------------------
Available modes:
  1. Generic    - Replace with placeholder values (XXX-XX-XXXX)
  2. Realistic  - Replace with realistic-looking but fake data  
  3. Custom     - Use custom replacement values from config

Select replacement mode (1-3): 2
```

#### Via Configuration File
```json
{
    "replacement_mode": "realistic"
}
```

#### Via API
```python
redactor = FinancialDocumentRedactor()
redactor.update_config({"replacement_mode": "realistic"})

# Or for custom mode with specific replacements
redactor.update_config({
    "replacement_mode": "custom",
    "replacement_settings": {
        "custom_replacements": {
            "ssn": "[CONFIDENTIAL-SSN]",
            "names": "[EMPLOYEE NAME]"
        }
    }
})
```

### Custom Patterns

Add custom redaction patterns to `config.json`:

```json
{
    "custom_patterns": [
        {
            "pattern": "\\b\\d{3}-\\d{3}-\\d{4}\\b",
            "replacement": "XXX-XXX-XXXX"
        }
    ]
}
```

## API Reference

### Core Classes

#### FinancialDocumentRedactor
Main redaction engine class.

```python
from core.redactor import FinancialDocumentRedactor

# Constructor
FinancialDocumentRedactor(config_path: str = None)
```

**Core Methods:**
- **`redact_pdf(input_pdf, output_pdf, input_folder, output_folder, user_patterns=None) -> bool`**
  - Redacts a single PDF file with document type detection and replacement mode support
  - Returns `True` if successful, `False` otherwise

- **`process_folder(input_folder, output_folder, user_patterns=None) -> Dict[str, int]`**
  - Processes all PDFs in a folder with progress tracking
  - Returns: `{'processed': int, 'failed': int, 'total': int}`

- **`detect_document_type(text: str) -> str`**
  - Detects document type: `'bank_statement'`, `'w2'`, `'tax_return'`, `'pay_stub'`, `'general'`

- **`get_enabled_patterns() -> List[Tuple[str, str]]`**
  - Returns currently enabled redaction patterns based on config and replacement mode

- **`update_config(updates: Dict[str, any], save: bool = True) -> Dict[str, any]`**
  - Update configuration including replacement mode settings

- **`add_custom_pattern(pattern: str, replacement: str, save: bool = True) -> bool`**
  - Add custom redaction pattern with regex validation

- **`get_document_info(pdf_path: str) -> Dict[str, any]`**
  - Get comprehensive PDF information including detected document type

#### RealisticDataGenerator
Generates realistic-looking replacement data.

```python
from utils.realistic_generators import RealisticDataGenerator

generator = RealisticDataGenerator(config)
realistic_ssn = generator.generate_ssn("123-45-6789")
realistic_name = generator.generate_person_name("John Smith")
realistic_phone = generator.generate_phone("(555) 123-4567")
```

### redactions.txt

For additional custom redactions, use the `redactions.txt` file:

```
Line 1: [text to redact]
Line 2: [replacement text]
Line 3: [leave empty]

Line 4: [next text to redact]
Line 5: [next replacement text]
Line 6: [leave empty]
```

## Usage Examples

### Basic CLI Usage
```bash
# Enhanced interactive experience with replacement mode selection
python redactor-cli.py
```

### Library Usage Examples

#### Basic Integration with Realistic Mode
```python
from core.redactor import FinancialDocumentRedactor

# Initialize with realistic replacements
redactor = FinancialDocumentRedactor()
redactor.update_config({"replacement_mode": "realistic"})

# Process folder - names will become "Michael Johnson" instead of "[NAME]"
results = redactor.process_folder(
    input_folder="/home/user/documents",
    output_folder="/home/user/redacted_docs"
)

print(f"Success: {results['processed']}, Failed: {results['failed']}")
```

#### Organization-Specific Custom Mode
```python
# Set up for corporate use
redactor = FinancialDocumentRedactor()
redactor.update_config({
    "replacement_mode": "custom",
    "replacement_settings": {
        "custom_replacements": {
            "ssn": "[SSN REDACTED PER COMPANY POLICY]",
            "names": "[EMPLOYEE NAME]",
            "phone": "[CONTACT INFO REDACTED]",
            "address": "[ADDRESS REDACTED]",
            "employer": "COMPANY CONFIDENTIAL"
        }
    }
})

results = redactor.process_folder("/hr_documents", "/redacted_hr")
```

#### Mode Comparison Testing
```python
redactor = FinancialDocumentRedactor()

# Test different modes
modes = ["generic", "realistic", "custom"]

for mode in modes:
    redactor.update_config({"replacement_mode": mode})
    output_folder = f"/output_{mode}"
    
    results = redactor.process_folder("/input", output_folder)
    print(f"{mode.title()} mode: {results['processed']} files processed")
```

### Project Structure
```
redactor/
├── core/                          # Core redaction engine
│   ├── redactor.py               # Main orchestration class
│   ├── document_detector.py      # Document type detection
│   └── pdf_processor.py          # PDF-specific operations with replacement modes
├── config/                        # Configuration & patterns
│   ├── manager.py                # Config loading/saving/validation
│   └── patterns.py               # Pattern definitions & replacement modes
├── cli/                          # User interface layer
│   ├── interface.py              # Interactive CLI with mode selection
│   └── utils.py                  # CLI utilities & file handling
├── utils/                        # Shared utilities
│   └── realistic_generators.py   # Realistic data generation
├── redactor_cli.py               # Legacy entry point
├── redactor-cli.py               # Main CLI entry point
├── redactor-gui.py               # Enhanced GUI interface
├── __main__.py                   # Module execution entry
├── setup.py                      # Package installation
├── config.json                   # Configuration (auto-created)
└── redactions.txt               # Custom patterns (auto-created)
```

## Enhanced CLI Features

**🎛️ Replacement Mode Selection**
- Interactive mode selection during setup
- Mode-specific tips and explanations
- Preview showing selected mode in processing summary

**👤 Name Redaction Control**
- Enable/disable name redaction through configuration
- Support for different name formats and contexts
- Consistent replacement of identical names

**📊 Enhanced Processing Preview**
```
🔍 Processing Preview
----------------------
📂 Input:  /documents/financial
📂 Output: /documents/redacted
⚙️  Level:  standard
🎛️  Mode:   Realistic
🔒 Enabled redactions: ssn, phone, account_number, names, email
```

## Output Examples

### Generic Mode Output
```
🔧 Loading configuration...
✅ Configuration loaded successfully

🎛️  Replacement Mode Selection
--------------------------------
Current mode: Generic

Available modes:
  1. Generic    - Replace with placeholder values (XXX-XX-XXXX, [REDACTED])
  2. Realistic  - Replace with realistic-looking but fake data
  3. Custom     - Use custom replacement values from config

Select replacement mode (1-3): 1
✅ Keeping current mode: Generic

📄 Found 3 PDF file(s) to process

🔍 Processing: bank_statement.pdf
📄 Detected document type: Bank Statement
✅ Redacted PDF saved as: bank_statement_redacted.pdf

📊 Results:
  ✅ Processed: 3
  ❌ Failed: 0
  📊 Total: 3
```

### Realistic Mode Benefits

**Document Readability**: Realistic mode maintains document structure while protecting privacy:
- Original: "John Smith's account (555) 123-4567 has balance $1,234.56"
- Generic: "[NAME]'s account (XXX) XXX-XXXX has balance $X,XXX.XX"  
- Realistic: "Michael Johnson's account (444) 555-7890 has balance $2,847.33"

**Consistent Replacements**: Same data always gets same realistic replacement within and across documents.

## Security Notes

- **Always verify redacted documents** before sharing
- **Test with sample documents** first to ensure proper redaction
- **Choose appropriate replacement mode** for your use case:
  - Generic: Maximum privacy, obvious redaction
  - Realistic: Maintains readability, fake but plausible data
  - Custom: Organization-specific compliance requirements
- **Keep original documents secure** and delete when no longer needed
- **Review config.json settings** to match your privacy requirements

## Troubleshooting

### Common Issues

1. **"File not found" errors**:
   - Ensure the folder name is correct
   - Check that PDFs are in the specified folder

2. **PyMuPDF import errors**:
   ```bash
   pip install --upgrade PyMuPDF
   ```

3. **Permission errors**:
   - Ensure write permissions to the directory
   - Close any open PDF files

4. **Redaction not working**:
   - Check that patterns are enabled in config.json
   - Verify custom regex patterns are valid
   - Test different replacement modes

5. **Names not being redacted**:
   - Ensure `"names": true` in enabled_categories
   - Check name patterns match your document format
   - Test with various name formats

## Migration Guide

### Upgrading to Latest Version

The new version maintains **100% backward compatibility** while adding powerful new features:

**✅ Existing Usage Still Works**
```bash
# Legacy entry point still available
python redactor_cli.py
```

**🆕 New Features Available**
- Multiple replacement modes (generic/realistic/custom)
- Advanced name redaction with context awareness
- Enhanced CLI with mode selection
- Improved realistic data generation
- Better consistency across documents

**📚 Enhanced Library Usage**
```python
# NEW: Replacement mode support
from core.redactor import FinancialDocumentRedactor
redactor = FinancialDocumentRedactor()
redactor.update_config({"replacement_mode": "realistic", "names": True})
results = redactor.process_folder("/input", "/output")
```

## Contributing

We welcome contributions! When contributing:

1. **Test thoroughly** with various document types and replacement modes
2. **Ensure patterns don't over-redact** - test with sample documents  
3. **Update documentation** for new features and API changes
4. **Follow the modular architecture** - keep core logic separate from UI
5. **Add unit tests** for new functionality
6. **Test realistic data generation** for consistency and safety
7. **Verify name redaction accuracy** across different formats

## License

This tool is provided as-is for legitimate document redaction purposes. Users are responsible for ensuring compliance with applicable privacy laws and regulations.