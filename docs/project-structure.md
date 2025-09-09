# 📁 Project Structure

## 🎯 Main Files

```
redactor/
├── redactor-gui.py               # 🖥️ Enhanced GUI interface (MAIN ENTRY)
├── redactor-cli.py               # 📋 Command line interface
├── README.md                     # 📚 Main documentation
├── config.json                   # ⚙️ Configuration settings
├── requirements.txt              # 📦 Python dependencies
└── setup.py                      # 📦 Package installer
```

## 📚 Documentation

```
docs/
├── quick-start.md               # 🚀 5-minute setup guide
├── user-guide.md                # 📖 Complete usage documentation  
├── project-summary.md           # 📋 Technical overview
└── project-structure.md         # 📁 This file
```

## 🧪 Testing Suite

```
tests/
├── test_quick.py               # ⚡ Fast development tests
├── test_nlp_names.py           # 🤖 NLP name detection tests
├── test_comprehensive.py       # 🔍 Complete test suite
├── test_patterns.py            # 📝 Pattern matching tests
├── test_regex_patterns.py      # 🔤 Legacy regex tests
└── README.md                   # 📚 Testing documentation
```

## 🔧 Core Engine

```
core/
├── redactor.py                 # 🎯 Main redaction logic
├── enhanced_processor.py       # 📊 Advanced processing with reporting
├── pdf_processor.py            # 📄 PDF manipulation
├── processors/                 # 📁 Document type processors
│   ├── base.py                 # 🏗️ Base processor class
│   ├── bank_statement.py       # 🏦 Bank statement processor
│   ├── w2.py                   # 📋 W2 form processor
│   ├── tax_return.py           # 📊 Tax return processor
│   └── pay_stub.py             # 💰 Pay stub processor
└── output_handlers/            # 📁 Output handling
    ├── base.py                 # 🏗️ Base output handler
    ├── pdf_handler.py          # 📄 PDF output
    └── text_handler.py         # 📝 Text output
```

## ⚙️ Configuration

```
config/
├── patterns.py                 # 🔍 Redaction patterns (with NLP integration)
└── manager.py                  # ⚙️ Configuration management
```

## 🛠️ Utilities

```
utils/
├── nlp_name_detector.py        # 🤖 NLP-powered name detection (NEW!)
└── realistic_generators.py     # 🎭 Realistic fake data generation
```

## 📊 Test Data

```
data/
└── input/                      # 📁 Sample test documents
    └── wells_fargo/            # 🏦 Wells Fargo test case
        └── wellsfargo.pdf      # 📄 Sample bank statement
```

## 🚀 CI/CD

```
.github/
└── workflows/
    └── build.yml               # 🔨 Cross-platform builds (Windows/Mac/Linux)
```

## 🎯 Usage Priority

### For Users:
1. **`redactor-gui.py`** - Start here! Full-featured GUI
2. **`docs/quick-start.md`** - 5-minute setup guide  
3. **`docs/user-guide.md`** - When you need more details

### For Developers:
1. **`tests/test_quick.py`** - Verify everything works
2. **`tests/test_nlp_names.py`** - Test name detection accuracy
3. **`core/`** - Core redaction engine
4. **`utils/nlp_name_detector.py`** - Advanced NLP detection

## 🎨 Key Features by File

| File | Key Feature |
|------|------------|
| `redactor-gui.py` | Modern GUI with tabs, progress tracking, detailed reports |
| `utils/nlp_name_detector.py` | 🤖 spaCy NLP for accurate name detection |
| `config/patterns.py` | Pattern definitions with NLP integration |
| `core/enhanced_processor.py` | Processing with comprehensive reporting |
| `tests/test_nlp_names.py` | Quality assurance for name detection |

## 🏃 Quick Commands

```bash
# Launch GUI
python redactor-gui.py

# Test setup
cd tests && python test_quick.py

# Test NLP accuracy  
cd tests && python test_nlp_names.py

# Process via CLI
python redactor-cli.py document.pdf
```

---

**💡 Tip**: Start with the GUI (`redactor-gui.py`) - it provides the best user experience with detailed feedback and reporting!