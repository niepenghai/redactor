# Project Memory - Financial Document Redactor

## Recent Major Updates

### Custom String Redaction Feature Implementation (Sep 22, 2024)

**Problem**: Users needed the ability to specify exact strings (names, addresses, company names) that should be redacted from financial documents, beyond the pre-defined pattern categories.

**Solution Implemented**:

#### 1. Core Custom String Management
- **File**: `core/redactor.py`
- **Methods Added**:
  - `add_custom_strings(strings, replacement, save)` - Add list of exact strings for redaction
  - `clear_custom_strings(save)` - Remove all custom strings
  - `get_custom_strings()` - Retrieve current custom strings
- **Integration**: Custom strings are converted to regex patterns with proper escaping and word boundaries

#### 2. Configuration System Enhancement
- **File**: `config/manager.py`
- **Changes Made**:
  - Added `"custom_strings": []` to default configuration
  - Added `get_custom_strings()` method for retrieving custom strings from config
- **Storage Format**: Each custom string stored as `{"text": "exact string", "replacement": "[CUSTOM_REDACTED]"}`

#### 3. Pattern Processing Integration
- **File**: `core/redactor.py` - `get_enabled_patterns()` method
- **Pattern Generation**:
  - Automatically escapes special regex characters with `re.escape()`
  - Adds word boundaries (`\b`) for alphanumeric strings
  - Integrates seamlessly with existing pattern pipeline
- **Category Recognition**: Custom strings recognized as `'custom_strings'` category in PDF processor

#### 4. PDF Processing Enhancement
- **File**: `core/pdf_processor.py`
- **Changes Made**:
  - Added `'custom_strings'` category to `_determine_pattern_category()` method
  - Custom string redactions logged separately: "Found X custom string match(es) on this page"
  - Full integration with balance filtering and overlap resolution systems

#### 5. Pattern Pipeline Fix
- **Critical Issue Resolved**: Custom patterns were being excluded from PDF processing pipeline
- **Root Cause**: `enabled_patterns` (containing custom strings) were not being passed to PDF processor
- **Solution**: Modified pattern combination logic to include both enabled patterns and document-specific patterns
- **Result**: Custom strings now flow correctly through entire redaction pipeline

#### 6. Testing and Validation
- **Basic Test Suite**: `test_custom_strings.py` - Tests string addition, duplicate handling, pattern integration, text redaction
- **Real PDF Test**: `test_custom_strings_on_pdf.py` - Tests actual PDF redaction with Bank of America statement
- **Comprehensive Testing**: Verified redaction of names, addresses, company names, and custom terms across 14-page PDF

#### 7. Results
- ✅ Custom strings are correctly converted to regex patterns with proper escaping
- ✅ Word boundaries prevent partial matches for alphanumeric strings
- ✅ Custom strings integrate seamlessly with existing balance preservation
- ✅ Multiple occurrences of custom strings are found and redacted across all pages
- ✅ Clean integration with existing pattern categories and replacement modes

**Usage Example**:
```python
redactor = FinancialDocumentRedactor()
custom_strings = ["John Smith", "ACME Corporation", "Project Alpha"]
redactor.add_custom_strings(custom_strings, "[CUSTOM_REDACTED]")
redactor.redact_pdf("input.pdf", "output.pdf", input_folder, output_folder)
```

**Example Output**:
```
🎯 Found 6 custom string match(es) on this page
🎯 Applied 8 custom string redaction(s) on this page
🎯 Custom redactions found: 12
📊 Original strings remaining: 0
✅ Custom string redaction successful!
```

### Balance Preservation Feature Implementation (Sep 20, 2024)

**Problem**: Users needed to preserve balance amounts (like account balances, beginning/ending balances) while redacting other currency amounts in financial documents.

**Solution Implemented**:

#### 1. Core Balance Detection Logic
- **File**: `config/patterns.py`
- **Functions Added**:
  - `is_balance_amount(text, start_pos, full_text)` - Detects if a currency amount is a balance that should be preserved
  - `filter_balance_amounts(matches, full_text)` - Filters out balance amounts from currency redaction matches

- **Detection Features**:
  - Context analysis within 200 characters before the amount
  - Supports multi-line formats (balance label on one line, amount on next line)
  - Recognizes various balance types: beginning balance, ending balance, available balance, current balance, account balance, total balance, statement balance, opening balance, closing balance

#### 2. PDF Processor Integration
- **File**: `core/pdf_processor.py`
- **Changes Made**:
  - Added imports for `filter_balance_amounts` and `is_balance_amount`
  - Modified `_redact_page()` method to collect all matches first, then apply balance filtering before redaction
  - Added `_determine_pattern_category()` method to categorize patterns by replacement text
  - Added balance filtering step with detailed logging

#### 3. Main Redactor Integration
- **File**: `core/redactor.py` and `core/pdf_processor.py`
- **Changes Made**:
  - Added balance filtering step in the redaction pipeline
  - Integrated with existing overlap resolution system

#### 4. Testing and Validation
- **Thoroughly tested** on Bank of America PDF with various balance formats
- **Verified preservation** of specific amounts: `$39,329.19`, `$7,800.00`, `$18,462.74`
- **Confirmed selective redaction** of non-balance currency amounts

#### 5. Results
- ✅ Balance amounts are correctly preserved during redaction
- ✅ Transaction amounts and other currency values are still redacted
- ✅ Multi-line balance formats are supported
- ✅ Context-aware detection prevents false positives
- ✅ Integration with existing realistic/generic replacement modes

**Usage**: Users can now run standard PDF redaction and balance amounts will automatically be preserved while other sensitive information is redacted.

**Example Output**:
```
🏦 Balance filtering: 21 → 18 matches (preserved 3 balance amounts)
🏦 Balance amounts preserved: 3
💰 Preserved balance examples: $18,462.74, $39,329.19, $7,800.00
```

## Previous Development History

### Cross-Platform Build System
- Implemented GitHub Actions workflow for Windows/macOS builds
- Added spaCy fallback mechanisms for Windows compatibility
- Created specialized Windows deployment packages

### NLP Integration
- Added spaCy-based name detection with SimpleNLP fallback
- Implemented hybrid address detection combining patterns and NLP
- Created realistic data generators for replacement modes

### Account Number Detection Enhancement
- Added support for space-separated account numbers (e.g., "0008 6117 4372")
- Enhanced regex patterns for various account number formats
- Improved Bank of America statement compatibility

## Architecture Notes

### PDF Redactor Core Workflow (Complete Analysis)

#### **1. Initialization & Configuration** (`FinancialDocumentRedactor.__init__`)
- Load configuration manager (ConfigurationManager)
- Initialize financial patterns (get_financial_patterns)
- Create document detector (DocumentTypeDetector)
- Initialize PDF processor (PDFProcessor)

#### **2. PDF Validation & Text Extraction** (`redact_pdf`)
- Validate PDF file integrity
- Extract complete document text for type detection
- Detect document type (bank_statement, w2, tax_return, pay_stub, general)

#### **3. Pattern Preparation & Filtering**
- Get enabled patterns based on configuration (get_enabled_patterns)
- Get document-specific patterns (get_patterns_for_document_type)
- Filter patterns by configuration (filter_patterns_by_config)
- Process replacement modes (generic/realistic/custom)

#### **4. Page-Level Redaction** (`_redact_page`)

**4.1 Pattern Enhancement:**
- Add NLP-detected name patterns (if names category enabled)
- Add hybrid address detection patterns (if address category enabled)
- Merge all detection patterns

**4.2 Match Collection:**
- Use `re.finditer()` on each pattern against page text
- Collect: (matched_text, replacement, start_pos, end_pos, category)
- Determine pattern category via `_determine_pattern_category()`

**4.3 Balance Filtering (NEW):**
- Apply `filter_balance_amounts()` to preserve balance amounts
- Log filtering results: "X → Y matches (preserved Z balance amounts)"
- Only filter currency category, preserve other redaction types

**4.4 Redaction Application:**
- Use `page.search_for()` to locate text positions in PDF
- Create redaction annotations with `page.add_redact_annot()`
- Apply all redactions with `page.apply_redactions()`
- Insert replacement text with `_insert_replacement_text()`

### Pattern Processing Pipeline (Enhanced)
1. **Pattern Collection**: Gather all regex patterns for enabled categories
2. **Match Detection**: Find all matches in document text using regex
3. **Balance Filtering**: Remove balance amounts from currency matches (NEW)
4. **Overlap Resolution**: Handle overlapping matches by priority
5. **Redaction Application**: Apply redactions to PDF with replacements

### Configuration System
- **12 Categories**: ssn, phone, account_number, routing_number, credit_card, tax_id, currency, dates, email, address, employer, names
- **Three replacement modes**: generic, realistic, custom
- **Document-specific patterns**: Different patterns for different document types
- **Balance preservation**: Works across all modes and document types
- **Fallback mechanisms**: Graceful degradation for missing dependencies (spaCy, etc.)

### PyMuPDF Integration Details

#### **Text Processing:**
- `page.get_text("text")` - Extract page text for pattern matching
- `page.search_for(text)` - Locate text rectangles in PDF coordinates

#### **Redaction Mechanism:**
- `page.add_redact_annot(rect, fill=(1,1,1))` - Add white-filled redaction annotation
- `page.apply_redactions()` - Permanently apply all redaction annotations
- `page.insert_htmlbox(rect, replacement)` - Insert styled replacement text

#### **Document Management:**
- `fitz.open(input_path)` - Open PDF for processing
- `doc.save(output_path)` - Save modified PDF with redactions
- Directory creation and comprehensive error handling

### Performance & Reliability Features

#### **Error Handling:**
- Regex pattern validation with detailed error messages
- PDF file integrity validation before processing
- Per-page processing with failure recovery
- Graceful fallback when optional dependencies unavailable

#### **Efficiency Optimizations:**
- Single text extraction per page, reused for all patterns
- Batch collection and processing of matches
- Overlap detection and resolution algorithms
- Lazy loading of NLP components (spaCy) when needed

#### **Logging & Monitoring:**
- Document type detection reporting
- NLP detection counts per page
- Balance filtering statistics
- Redaction success/failure tracking

### Key Implementation Strengths

#### **Modular Architecture:**
- Clear separation between detection (patterns), processing (pdf_processor), and orchestration (redactor)
- Pluggable NLP components with fallback mechanisms
- Independent document type detection system

#### **Extensibility:**
- Easy to add new pattern categories in `patterns.py`
- Document-specific pattern customization
- Multiple replacement mode support (generic/realistic/custom)

#### **Robustness:**
- Comprehensive error handling at each processing stage
- Graceful degradation when dependencies unavailable
- Regex validation and safe pattern processing

#### **Balance Preservation Innovation:**
- Context-aware detection (200 characters analysis)
- Multi-line format support (label and amount on different lines)
- Conservative filtering approach (only affects currency category)
- Seamless integration without breaking existing functionality

## Technical Decisions Made

### Balance Detection Approach
- **Context-based** rather than strict regex patterns to handle various document formats
- **Multi-line support** for cases where balance labels and amounts are on separate lines
- **Conservative filtering** - only filters currency category, preserves other redaction types
- **Backwards compatible** - works with existing redaction pipeline without breaking changes

### Integration Strategy
- **Minimal invasive changes** - added filtering step without restructuring existing code
- **Integrated functionality** - works in the main redaction pipeline
- **Graceful degradation** - continues working even if balance filtering functions are unavailable

## Future Considerations

### Potential Enhancements
- Add configuration option to enable/disable balance preservation
- Support for additional balance keywords in other languages
- Integration with document type detection for balance-specific rules
- Enhanced logging and reporting of preserved vs redacted amounts

### Maintenance Notes
- Balance detection keywords may need updates for different financial institutions
- Pattern category mapping in `_determine_pattern_category()` should be kept in sync with `patterns.py`
- Consider adding unit tests for balance detection edge cases

## Files Modified

### Custom String Redaction (Sep 22, 2024)
- `core/redactor.py` - Added custom string management methods and pattern integration
- `config/manager.py` - Enhanced configuration system with custom strings support
- `core/pdf_processor.py` - Added custom string category recognition and pattern pipeline fix
- `test_custom_strings.py` - Basic functionality test suite
- `test_custom_strings_on_pdf.py` - Real PDF redaction test with Bank of America statement

### Balance Preservation (Sep 20, 2024)
- `config/patterns.py` - Added balance detection and filtering functions
- `core/pdf_processor.py` - Integrated balance filtering into redaction pipeline
- `core/pdf_processor.py` - Added balance filtering support
- Test files cleaned up after implementation validation

## Sample Output
- `sample_redacted_with_balance_preserved.pdf` - Working example demonstrating the feature