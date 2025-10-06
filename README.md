# 📄 Financial Document Redactor

> **A Python application for automatically redacting sensitive information from financial documents**

[![GitHub Release](https://img.shields.io/github/v/release/niepenghai/redactor)](https://github.com/niepenghai/redactor/releases)
[![Build Status](https://github.com/niepenghai/redactor/workflows/Build%20Cross-Platform%20Executables/badge.svg)](https://github.com/niepenghai/redactor/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🚀 Quick Start

### Download Ready-to-Use Applications

**No Python installation required!** Download pre-built executables:

- 🪟 **Windows**: [PDF-Redactor-Windows-Offline.zip](https://github.com/niepenghai/redactor/releases/latest)
- 🍎 **macOS**: [PDFRedactor-macOS.zip](https://github.com/niepenghai/redactor/releases/latest)

### Run from Source

```bash
# Clone the repository
git clone https://github.com/niepenghai/redactor.git
cd redactor

# Install dependencies
pip install -r requirements.txt

# Launch GUI
python redactor-gui.py

# Or use main entry point
python main.py
```

## ✨ Features

- 📋 **Multiple Document Types**: Bank statements, W2 forms, tax returns, pay stubs
- 🎯 **Smart Detection**: Automatically finds SSNs, account numbers, names, addresses
- 🔧 **Multiple Modes**:
  - **Generic**: Replace with generic placeholders (`[REDACTED]`)
  - **Realistic**: Replace with realistic fake data
  - **Custom**: Use your own replacement patterns
- 💻 **Cross-Platform**: Windows, macOS, Linux support
- 🖥️ **Modern GUI**: Easy-to-use graphical interface
- ⚡ **Fast Processing**: Efficient PDF processing with real-time progress

## 📁 Project Structure

```
redactor/
├── main.py                    # Main entry point
├── redactor-gui.py           # GUI application
├── core/                     # Core redaction engine
│   ├── redactor.py          # Main redaction logic
│   ├── pdf_processor.py     # PDF processing
│   └── document_detector.py # Document type detection
├── config/                   # Configuration management
│   ├── manager.py           # Config loading/saving
│   └── patterns.py          # Redaction patterns
├── utils/                    # Utility functions
│   ├── realistic_generators.py
│   ├── address_detector.py
│   └── nlp_name_detector.py
├── scripts/                  # Build scripts
│   ├── redactor.spec        # macOS build config
│   ├── redactor-windows.spec # Windows build config
│   └── build-local.sh       # Local build script
├── windows-deployment/       # Windows deployment files
├── docs/                     # Documentation
└── tests/                    # Test files
```

## 🛠️ Development

### Prerequisites

- Python 3.9+
- PyMuPDF (for PDF processing)
- tkinter (for GUI, usually included with Python)
- Additional dependencies in `requirements.txt`

### Building Executables

```bash
# macOS
cd scripts/
pyinstaller redactor.spec

# Windows  
cd scripts/
pyinstaller redactor-windows.spec

# Or use automated script
./scripts/build-local.sh
```

### Platform Differences

| Platform | spaCy Support | NLP Features | Build Size |
|----------|---------------|--------------|------------|
| **macOS** | ✅ Full | Advanced NLP detection | ~600MB |
| **Windows** | ❌ Fallback | Rule-based detection | ~200MB |

*Windows uses SimpleNLP fallback due to spaCy compilation issues*

## 📚 Usage Examples

### GUI Interface
```bash
python redactor-gui.py
```
1. Select PDF files
2. Choose output directory  
3. Select redaction mode
4. Click "Process Files"

### Programmatic Usage
```python
from core.redactor import FinancialDocumentRedactor

redactor = FinancialDocumentRedactor()
result = redactor.process_file(
    input_path="bank_statement.pdf",
    output_path="redacted_statement.pdf",
    mode="realistic"
)
print(f"Processed: {result.num_redactions} redactions")
```

## 🔧 Configuration

The application automatically creates configuration files:
- `config.json` - Main settings (auto-generated)
- `redactions.txt` - Custom patterns (optional)

### Supported Document Types

- **Bank Statements**: Account numbers, balances, transaction details
- **W2 Forms**: SSN, employer info, wages
- **Tax Returns**: Personal information, financial data
- **Pay Stubs**: Employee details, salary information

## 🚀 Deployment

### Windows Offline Deployment
1. Download `PDF-Redactor-Windows-Offline.zip`
2. Extract to desired location
3. Run `启动程序.bat`

### macOS Deployment  
1. Download `PDFRedactor-macOS.zip`
2. Extract and double-click `PDFRedactor.app`
3. Right-click → "Open" if security warning appears

## 🧪 Testing

```bash
# Run tests (if available)
python -m pytest tests/

# Manual testing
python main.py --help
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- [📥 Latest Release](https://github.com/niepenghai/redactor/releases/latest)
- [🐛 Report Issues](https://github.com/niepenghai/redactor/issues)
- [📖 Documentation](docs/)

## 🙏 Acknowledgments

- PyMuPDF for PDF processing
- spaCy for natural language processing (macOS)
- tkinter for GUI framework

---

**⚠️ Important**: This tool is for legitimate document redaction purposes only. Always verify redacted documents before sharing.