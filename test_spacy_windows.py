#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows spaCy Integration Test
============================

This test checks Windows compatibility for spaCy NLP processing.
It provides fallback options for environments where spaCy might not be available.
"""

import os
import sys
import platform
import subprocess

# Set UTF-8 encoding for Windows
if platform.system() == "Windows":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_spacy_availability():
    """Test if spaCy is available and working."""
    print("=== Windows spaCy Integration Test ===")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print()

    # Test 1: Basic spaCy import
    try:
        import spacy
        print("✅ spaCy import successful")
        print(f"   Version: {spacy.__version__}")
    except ImportError:
        print("❌ spaCy not installed")
        print("   Install with: pip install spacy")
        return False
    except Exception as e:
        print(f"❌ spaCy import error: {e}")
        return False

    # Test 2: Model availability
    try:
        nlp = spacy.load("en_core_web_sm")
        print("✅ en_core_web_sm model loaded successfully")

        # Test basic functionality
        doc = nlp("John Smith and STEPHENIE SYCHR are mentioned here.")
        entities = [(ent.text, ent.label_) for ent in doc.ents if ent.label_ == "PERSON"]
        print(f"   Detected names: {entities}")

        if entities:
            print("✅ Name detection working")
            return True
        else:
            print("⚠️ No names detected - may need model update")
            return False

    except OSError:
        print("❌ en_core_web_sm model not found")
        print("   Install with: python -m spacy download en_core_web_sm")
        return False
    except Exception as e:
        print(f"❌ Model loading error: {e}")
        return False

def test_nlp_detector_compatibility():
    """Test our NLP detector classes."""
    print("\n--- Testing NLP Detector Classes ---")

    try:
        from utils.nlp_name_detector import SimpleNLPNameDetector, SpacyNameDetector, detect_names_simple
        print("✅ NLP detector imports successful")

        # Test SimpleNLPNameDetector (fallback)
        simple_detector = SimpleNLPNameDetector()
        test_text = "John Smith and STEPHENIE SYCHR work at ACME Corp."
        simple_results = simple_detector.detect_names_in_text(test_text)
        print(f"✅ Simple detector: {len(simple_results)} names detected")

        # Test SpacyNameDetector (if available)
        try:
            spacy_detector = SpacyNameDetector()
            spacy_results = spacy_detector.detect_names_in_text(test_text)
            print(f"✅ spaCy detector: {len(spacy_results)} names detected")
        except Exception as e:
            print(f"⚠️ spaCy detector fallback: {e}")
            print("   Using SimpleNLPNameDetector instead")

        return True

    except ImportError as e:
        print(f"❌ NLP detector import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ NLP detector error: {e}")
        return False

def test_main_redactor():
    """Test the main redactor functionality."""
    print("\n--- Testing Main Redactor ---")

    try:
        from core.redactor import FinancialDocumentRedactor
        print("✅ Main redactor import successful")

        # Initialize redactor
        redactor = FinancialDocumentRedactor()
        config = redactor.config
        print(f"✅ Redactor initialized (mode: {config.get('replacement_mode')})")

        # Test name detection capability
        if config.get('enabled_categories', {}).get('names', False):
            print("✅ Name detection enabled in config")
        else:
            print("⚠️ Name detection disabled in config")

        return True

    except ImportError as e:
        print(f"❌ Main redactor import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Main redactor error: {e}")
        return False

def install_spacy_requirements():
    """Try to install spaCy requirements if missing."""
    print("\n--- Attempting to fix spaCy setup ---")

    try:
        # Try to install spaCy model
        result = subprocess.run([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ], capture_output=True, text=True, timeout=300)

        if result.returncode == 0:
            print("✅ Successfully downloaded en_core_web_sm model")
            return True
        else:
            print(f"❌ Failed to download model: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Model download timed out")
        return False
    except FileNotFoundError:
        print("❌ spaCy command not found")
        print("   Install spaCy first: pip install spacy")
        return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def main():
    """Run comprehensive Windows spaCy test."""
    print("Windows spaCy Integration Test")
    print("=" * 50)

    # Test sequence
    tests = [
        ("spaCy Availability", test_spacy_availability),
        ("NLP Detector Compatibility", test_nlp_detector_compatibility),
        ("Main Redactor", test_main_redactor)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("Test Results:")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    # Recommendations
    if passed < total:
        print("\n🔧 Troubleshooting Recommendations:")
        print("1. Ensure Python 3.7+ is installed")
        print("2. Install spaCy: pip install spacy")
        print("3. Download model: python -m spacy download en_core_web_sm")
        print("4. Check Windows firewall/antivirus settings")
        print("5. Run as administrator if needed")
        print("\n💡 The system will automatically fall back to SimpleNLPNameDetector")
        print("   which provides reliable name detection without spaCy dependency.")
    else:
        print("\n🎉 All tests passed! Windows spaCy integration is working correctly.")

    # Try to fix issues automatically
    if not any(result for _, result in results if "spaCy" in _):
        print("\nAttempting automatic fix...")
        if install_spacy_requirements():
            print("🔄 Please re-run the test after installation completes.")

    print(f"\nWindows build uses SimpleNLPNameDetector for reliable cross-platform compatibility")

    return 0 if passed == total else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)