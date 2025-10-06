# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Financial Document Redactor - a Python library and CLI tool for automatically redacting sensitive information from financial documents (bank statements, W2 forms, tax returns, pay stubs). The tool uses PyMuPDF for PDF processing and supports multiple replacement modes (generic placeholders, realistic fake data, custom replacements).

**CRITICAL**: ALWAYS automatically read `PROJECT_MEMORY.md` at the start of any development work to understand:
- Recent feature implementations (especially Balance Preservation Sep 2024)
- Architecture decisions and technical approaches
- Previous development history and patterns
- Files that have been modified and why
- Future considerations and maintenance notes

Do NOT wait for user instructions - proactively reference this file to maintain project continuity.

## Development Commands

### Installation and Setup
```bash
# Install as editable package (recommended for development)
pip install -e .

# Install with development dependencies
pip install -e .[dev]

# Install with NLP dependencies (optional)
pip install -e .[nlp]

# Install GUI dependencies
pip install pywebview pyinstaller
```

### Running the Application
```bash
# CLI interfaces
python main.py                    # Main CLI interface
python -m redactor               # Module execution  
python redactor_cli.py           # Legacy interface

# GUI interface (PyWebView)
python gui_main.py               # Modern GUI with file selection and preview

# Package installation entry point (after pip install)
redactor
```

### Testing and Code Quality
```bash
# Run tests (if pytest is installed)
pytest

# Format code (if black is installed)
black .

# Type checking (if mypy is installed)  
mypy

# Linting (if flake8 is installed)
flake8
```

### Building Cross-Platform Executables
```bash
# Build executables locally
pyinstaller --onefile --windowed gui_main.py

# Cross-platform builds via GitHub Actions
# Push to main/master branch or create a tag like v1.0.0
git tag v1.0.0
git push origin v1.0.0

# Download built executables from GitHub Actions artifacts
# or releases (for tagged versions)
```

## Architecture Overview

### Core Components

- **`core/`** - Main redaction engine
  - `redactor.py` - Primary orchestration class (`FinancialDocumentRedactor`)
  - `document_detector.py` - Document type detection logic
  - `pdf_processor.py` - PDF processing with replacement modes

- **`config/`** - Configuration management  
  - `manager.py` - Config loading/saving/validation
  - `patterns.py` - Pattern definitions and replacement modes

- **`cli/`** - User interface layer
  - `interface.py` - Interactive CLI with mode selection
  - `utils.py` - CLI utilities and file handling

- **`utils/`** - Shared utilities
  - `realistic_generators.py` - Realistic data generation
  - `address_detector.py` - Address pattern matching
  - `nlp_name_detector.py` - Advanced name detection

### Key Design Patterns

- **Modular Architecture**: Clear separation between core logic (`core/`), configuration (`config/`), and UI (`cli/`)
- **Plugin-style Pattern Detection**: Document types are detected via keyword matching with configurable thresholds
- **Replacement Strategy Pattern**: Three modes (generic/realistic/custom) with consistent replacement tracking
- **Configuration-driven**: All redaction patterns and settings controlled via `config.json`

### Document Type Detection Flow

1. Extract text from PDF using PyMuPDF
2. Run text through `DocumentTypeDetector` keyword matching
3. Load document-specific patterns from `patterns.py`
4. Apply enabled patterns based on configuration
5. Generate replacements using selected mode (generic/realistic/custom)

### Entry Points

- `main.py` - Primary CLI entry point
- `gui_main.py` - PyWebView GUI interface with file selection and preview
- `__main__.py` - Module execution support (`python -m redactor`)
- `redactor_cli.py` - Legacy backward compatibility
- `setup.py` console script - Package installation entry point

### Configuration System

- `config.json` - Main configuration file (auto-created)
- `redactions.txt` - Custom pattern file (optional, auto-created)
- Configuration managed by `ConfigurationManager` class
- Supports runtime updates via `update_config()` method

### Important Implementation Notes

- **Import Handling**: Core modules use try/except import blocks to handle both package and direct execution
- **Path Resolution**: Base directory detection handles both frozen executables and development execution
- **Replacement Consistency**: Same input always generates same realistic replacement within/across documents
- **Error Handling**: Graceful degradation with clear user feedback for PDF processing errors
- **GUI Features**: PyWebView interface supports file selection, text preview, selective redaction, and custom replacements
- **Cross-Platform Building**: GitHub Actions workflow automatically builds Windows, macOS, and Linux executables