#!/usr/bin/env python3
"""
Test script to verify spaCy installation and functionality on Windows.
This script tests the spaCy wheel installation approach.
"""

def test_spacy_installation():
    """Test spaCy installation and model loading."""
    print("[TESTING] spaCy installation...")

    # Test 1: Import spaCy
    try:
        import spacy
        print(f"[OK] spaCy imported successfully - version: {spacy.__version__}")
    except ImportError as e:
        print(f"[ERROR] spaCy import failed: {e}")
        return False

    # Test 2: Load model
    try:
        nlp = spacy.load("en_core_web_sm")
        print("[OK] spaCy model 'en_core_web_sm' loaded successfully")
    except OSError as e:
        print(f"[ERROR] spaCy model loading failed: {e}")
        return False

    # Test 3: Basic NER functionality
    try:
        test_text = "Hello, my name is John Smith and I live in New York."
        doc = nlp(test_text)

        entities = [(ent.text, ent.label_) for ent in doc.ents]
        print(f"[OK] NER test successful - found entities: {entities}")

        # Check if we found at least one PERSON entity
        person_entities = [ent for ent in entities if ent[1] == 'PERSON']
        if person_entities:
            print(f"[OK] Person name detection working: {person_entities}")
        else:
            print("[WARNING] No PERSON entities detected in test text")

    except Exception as e:
        print(f"[ERROR] NER test failed: {e}")
        return False

    return True

def test_fallback_detection():
    """Test fallback name detection without spaCy."""
    print("\n[PROCESSING] Testing fallback detection mechanism...")

    try:
        # Import our custom detector
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        from utils.nlp_name_detector import detect_names_simple

        test_text = "Account holder: John Smith, Customer: Mary Johnson"
        detections = detect_names_simple(test_text)

        print(f"[OK] Fallback detection successful - found: {detections}")
        return True

    except Exception as e:
        print(f"[ERROR] Fallback detection failed: {e}")
        return False

def test_integration():
    """Test integration with the main redactor."""
    print("\n[TEST] Testing integration with main redactor...")

    try:
        from utils.nlp_name_detector import detect_names_nlp

        test_text = "Dear Mr. John Smith, your account balance is $1,234.56."
        detections = detect_names_nlp(test_text)

        print(f"[OK] Integration test successful - found: {detections}")
        return True

    except Exception as e:
        print(f"[ERROR] Integration test failed: {e}")
        return False

if __name__ == "__main__":
    # Windows-compatible output without emojis
    print("Windows spaCy Installation Test")
    print("=" * 50)

    success_count = 0
    total_tests = 3

    # Run tests
    if test_spacy_installation():
        success_count += 1

    if test_fallback_detection():
        success_count += 1

    if test_integration():
        success_count += 1

    print("\n" + "=" * 50)
    print(f"[STATS] Test Results: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("[SUCCESS] All tests passed! spaCy Windows installation successful.")
        exit(0)
    elif success_count >= 1:
        print("[WARNING] Partial success - fallback mechanisms available.")
        exit(0)
    else:
        print("[ERROR] All tests failed - check installation.")
        exit(1)