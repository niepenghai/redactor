# 🚀 Quick Start Guide

Get started with the PDF Document Redactor in under 5 minutes!

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd redactor

# Install dependencies
pip install PyMuPDF spacy
python -m spacy download en_core_web_sm
```

## 🖥️ Launch GUI (Recommended)

```bash
python redactor-gui.py
```

1. **Select PDF Files** - Click "📂 Select PDF Files" 
2. **Choose Output Folder** - Click "📁 Select Output Folder"
3. **Start Processing** - Click "🔒 Process X File(s)"
4. **View Results** - Check the three tabs for detailed reports

## 📋 Command Line Usage

```bash
# Process a single PDF
python redactor-cli.py path/to/document.pdf

# Process multiple PDFs
python redactor-cli.py folder/*.pdf

# Custom output directory
python redactor-cli.py document.pdf --output ./redacted/
```

## 🎯 What Gets Redacted?

✅ **Personal Names** (XIA LIN, John Smith, Dr. Brown)  
✅ **SSNs** (123-45-6789)  
✅ **Phone Numbers** ((555) 123-4567)  
✅ **Addresses** (123 Main St, City, State ZIP)  
✅ **Account Numbers** (Bank accounts, credit cards)  
✅ **Email Addresses** (user@domain.com)  

❌ **Avoids False Positives**: Bank names, street names, business terms

## 🧪 Test It Out

```bash
# Test with sample files
cd tests
python test_quick.py

# Test NLP name detection
python test_nlp_names.py
```

## 📚 Next Steps

- Read the full [User Guide](user-guide.md)
- Check the [Project Summary](project-summary.md)
- View configuration options in `config.json`

## ❓ Need Help?

- GUI not working? Check you have all dependencies installed
- Names not detected? Verify spaCy is installed: `python -c "import spacy; spacy.load('en_core_web_sm')"`
- False positives? Our NLP system should prevent these - run tests to verify

Happy redacting! 🔒