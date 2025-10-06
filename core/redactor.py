"""
Core redaction engine for financial documents.
"""
import os
import sys
import re
from typing import List, Tuple, Dict

# Handle both package and direct execution imports
try:
    from .document_detector import DocumentTypeDetector
    from .pdf_processor import PDFProcessor
    from ..config.manager import ConfigurationManager
    from ..config.patterns import get_financial_patterns, get_patterns_for_document_type, filter_patterns_by_config, get_enhanced_patterns, get_pattern_generators
    from ..utils.realistic_generators import RealisticDataGenerator
except ImportError:
    # Add parent directory to path for direct execution
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.document_detector import DocumentTypeDetector
    from core.pdf_processor import PDFProcessor
    from config.manager import ConfigurationManager
    from config.patterns import get_financial_patterns, get_patterns_for_document_type, filter_patterns_by_config, get_enhanced_patterns, get_pattern_generators
    from utils.realistic_generators import RealisticDataGenerator


class FinancialDocumentRedactor:
    """Main class for redacting sensitive information from financial documents."""
    
    def __init__(self, config_path: str = None):
        """Initialize the redactor with optional config path."""
        self.base_dir = self._get_base_dir()
        self.config_manager = ConfigurationManager(self.base_dir)
        self.config = self.config_manager.load_config(config_path)
        self.financial_patterns = get_financial_patterns()
        self.document_detector = DocumentTypeDetector()
        self.pdf_processor = PDFProcessor(self.config)
        
    def _get_base_dir(self) -> str:
        """Get the base directory for the application."""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def detect_document_type(self, text: str) -> str:
        """
        Detect the type of financial document based on content.
        
        Args:
            text: Document text content
            
        Returns:
            Document type string
        """
        return self.document_detector.detect_document_type(text)
    
    def get_patterns_for_document_type(self, doc_type: str) -> List[Tuple[str, str]]:
        """
        Get specific redaction patterns based on document type.
        
        Args:
            doc_type: Type of document
            
        Returns:
            List of (pattern, replacement) tuples
        """
        return get_patterns_for_document_type(doc_type, self.financial_patterns)
    
    def get_enabled_patterns(self, debug: bool = False) -> List[Tuple[str, str]]:
        """Get only the enabled patterns based on configuration and replacement mode."""
        enabled_patterns = []
        enabled_categories = self.config_manager.get_enabled_categories(self.config)
        replacement_mode = self.config.get("replacement_mode", "generic")
        
        # Get enhanced patterns based on replacement mode
        if replacement_mode == "realistic" and RealisticDataGenerator:
            enhanced_patterns = get_enhanced_patterns(self.config)
            for category, patterns in enhanced_patterns.items():
                if enabled_categories.get(category, True):
                    enabled_patterns.extend(patterns)
        elif replacement_mode == "custom":
            enhanced_patterns = get_enhanced_patterns(self.config)
            for category, patterns in enhanced_patterns.items():
                if enabled_categories.get(category, True):
                    enabled_patterns.extend(patterns)
        else:
            # Default generic mode
            for category, patterns in self.financial_patterns.items():
                if enabled_categories.get(category, True):
                    enabled_patterns.extend(patterns)
        
        # Add custom patterns from config
        custom_patterns = self.config_manager.get_custom_patterns(self.config)
        for custom_pattern in custom_patterns:
            enabled_patterns.append((custom_pattern["pattern"], custom_pattern["replacement"]))

        # Add custom strings as exact match patterns
        custom_strings = self.config_manager.get_custom_strings(self.config)
        for custom_string in custom_strings:
            # Escape the string for exact matching
            escaped_text = re.escape(custom_string["text"])
            # Use word boundaries only if the string starts/ends with word characters
            if escaped_text and escaped_text[0].isalnum() and escaped_text[-1].isalnum():
                pattern = f"\\b{escaped_text}\\b"
            else:
                pattern = escaped_text
            enabled_patterns.append((pattern, custom_string["replacement"]))

        return enabled_patterns
    
    def redact_pdf(self, input_pdf: str, output_pdf: str, input_folder: str, output_folder: str, user_patterns: List[Tuple[str, str]] = None) -> bool:
        """
        Redact sensitive information from a PDF file.
        
        Args:
            input_pdf: Input PDF filename
            output_pdf: Output PDF filename
            input_folder: Input directory path
            output_folder: Output directory path
            user_patterns: Optional additional patterns
            
        Returns:
            True if successful, False otherwise
        """
        if user_patterns is None:
            user_patterns = []
            
        input_path = os.path.join(input_folder, input_pdf)
        output_path = os.path.join(output_folder, output_pdf)
        
        print(f"🔍 Processing: {input_pdf}")
        
        # Validate input PDF
        is_valid, error_msg = self.pdf_processor.validate_pdf(input_path)
        if not is_valid:
            print(f"❌ {error_msg}")
            return False
        
        try:
            # Extract text for document type detection
            all_text = self.pdf_processor.extract_text_from_pdf(input_path)
            
            # Detect document type
            doc_type = self.detect_document_type(all_text)
            print(f"📄 Detected document type: {doc_type.replace('_', ' ').title()}")
            
            # Get enabled patterns based on configuration (includes custom strings)
            enabled_patterns = self.get_enabled_patterns()

            # Get document-specific patterns
            document_patterns = self.get_patterns_for_document_type(doc_type)

            # Filter document patterns based on config
            filtered_doc_patterns = filter_patterns_by_config(document_patterns, enabled_patterns)

            # Combine enabled patterns (includes custom strings) with filtered document patterns
            # Note: enabled_patterns already includes all patterns we want, including custom strings
            all_enabled_patterns = enabled_patterns + filtered_doc_patterns

            # Remove duplicates while preserving order
            seen = set()
            unique_patterns = []
            for pattern, replacement in all_enabled_patterns:
                if (pattern, replacement) not in seen:
                    unique_patterns.append((pattern, replacement))
                    seen.add((pattern, replacement))

            # Process patterns for realistic replacements if needed
            processed_patterns = self._process_patterns_for_replacement(unique_patterns, all_text)

            # Combine with user-defined patterns
            combined_patterns = processed_patterns + user_patterns
            
            # Apply redaction
            success = self.pdf_processor.redact_pdf_file(input_path, output_path, combined_patterns)
            
            if success:
                print(f"✅ Redacted PDF saved as: {output_pdf}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error processing PDF {input_pdf}: {str(e)}")
            return False
    
    def process_folder(self, input_folder: str, output_folder: str, user_patterns: List[Tuple[str, str]] = None) -> Dict[str, int]:
        """
        Process all PDFs in a folder.
        
        Args:
            input_folder: Input directory path
            output_folder: Output directory path
            user_patterns: Optional additional patterns
            
        Returns:
            Dictionary with processing statistics
        """
        if user_patterns is None:
            user_patterns = []
            
        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)
        
        print(f"\n🚀 Starting financial document redaction...")
        print(f"📁 Input folder: {input_folder}")
        print(f"📁 Output folder: {output_folder}")
        print(f"⚙️  Redaction level: {self.config['redaction_level']}")

        # Find PDF files
        try:
            pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]
        except OSError as e:
            print(f"❌ Error accessing input folder: {str(e)}")
            return {'processed': 0, 'failed': 0, 'total': 0}
        
        print(f"📄 Found {len(pdf_files)} PDF file(s) to process")

        processed_count = 0
        failed_count = 0

        for filename in pdf_files:
            file_path = os.path.join(input_folder, filename)
            if os.path.isfile(file_path):
                # Generate output filename
                name_without_ext = filename[:filename.rfind('.pdf')] if '.pdf' in filename else filename
                output_filename = f"{name_without_ext}_redacted.pdf"
                
                if self.redact_pdf(filename, output_filename, input_folder, output_folder, user_patterns):
                    processed_count += 1
                else:
                    failed_count += 1

        return {
            'processed': processed_count,
            'failed': failed_count,
            'total': len(pdf_files)
        }
    
    def update_config(self, updates: Dict[str, any], save: bool = True) -> Dict[str, any]:
        """
        Update configuration settings.
        
        Args:
            updates: Dictionary of configuration updates
            save: Whether to save changes to file
            
        Returns:
            Updated configuration
        """
        self.config = self.config_manager.update_config(updates, save)
        # Update PDF processor with new config
        self.pdf_processor = PDFProcessor(self.config)
        return self.config
    
    def get_config(self) -> Dict[str, any]:
        """Get current configuration."""
        return self.config.copy()
    
    def add_custom_pattern(self, pattern: str, replacement: str, save: bool = True) -> bool:
        """
        Add a custom redaction pattern.
        
        Args:
            pattern: Regular expression pattern
            replacement: Replacement text
            save: Whether to save to config file
            
        Returns:
            True if successful
        """
        try:
            # Test the pattern to ensure it's valid
            import re
            re.compile(pattern)
            
            # Add to config
            custom_patterns = self.config_manager.get_custom_patterns(self.config)
            custom_patterns.append({"pattern": pattern, "replacement": replacement})
            
            updates = {"custom_patterns": custom_patterns}
            self.update_config(updates, save)
            
            return True
        except re.error as e:
            print(f"❌ Invalid regex pattern '{pattern}': {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Error adding custom pattern: {str(e)}")
            return False

    def add_custom_strings(self, strings: List[str], replacement: str = "[REDACTED]", save: bool = True) -> bool:
        """
        Add custom strings for exact text redaction.

        Args:
            strings: List of exact strings to redact
            replacement: Replacement text for all strings
            save: Whether to save the config to file

        Returns:
            True if successful, False otherwise
        """
        try:
            if not strings:
                print("❌ No strings provided")
                return False

            # Get existing custom strings from config
            custom_strings = self.config.get("custom_strings", [])

            # Add new strings (avoid duplicates)
            added_count = 0
            for string in strings:
                if string and string.strip():  # Skip empty strings
                    string_data = {
                        "text": string.strip(),
                        "replacement": replacement
                    }
                    # Check for duplicates
                    if not any(item["text"] == string_data["text"] for item in custom_strings):
                        custom_strings.append(string_data)
                        added_count += 1

            updates = {"custom_strings": custom_strings}
            self.update_config(updates, save)

            print(f"✅ Added {added_count} custom strings for redaction")
            return True

        except Exception as e:
            print(f"❌ Error adding custom strings: {str(e)}")
            return False

    def clear_custom_strings(self, save: bool = True) -> bool:
        """
        Clear all custom strings.

        Args:
            save: Whether to save the config to file

        Returns:
            True if successful, False otherwise
        """
        try:
            updates = {"custom_strings": []}
            self.update_config(updates, save)
            print("✅ Cleared all custom strings")
            return True
        except Exception as e:
            print(f"❌ Error clearing custom strings: {str(e)}")
            return False

    def get_custom_strings(self) -> List[Dict[str, str]]:
        """
        Get current custom strings.

        Returns:
            List of custom string dictionaries
        """
        return self.config.get("custom_strings", [])

    def generate_realistic_replacement(self, category: str, original_text: str) -> str:
        """Generate realistic replacement for GUI preview."""
        try:
            from ..utils.realistic_generators import RealisticDataGenerator
        except ImportError:
            from utils.realistic_generators import RealisticDataGenerator

        generator = RealisticDataGenerator(self.config)

        if category == 'ssn':
            return generator.generate_ssn(original_text)
        elif category == 'phone':
            return generator.generate_phone(original_text)
        elif category == 'names':
            return generator.generate_person_name(original_text)
        elif category == 'email':
            return generator.generate_email(original_text)
        elif category == 'address':
            return generator.generate_address(original_text)
        elif category == 'account_number':
            return generator.generate_account_number(original_text)
        elif category == 'routing_number':
            return generator.generate_routing_number(original_text)
        elif category == 'credit_card':
            return generator.generate_credit_card(original_text)
        elif category == 'tax_id':
            return generator.generate_tax_id(original_text)
        elif category == 'currency':
            return generator.generate_currency(original_text)
        elif category == 'dates':
            return generator.generate_date(original_text)
        else:
            # Fallback to generic replacement
            return f"[{category.upper()}]"

    def get_document_info(self, pdf_path: str) -> Dict[str, any]:
        """
        Get information about a PDF document.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with document information
        """
        info = self.pdf_processor.get_pdf_info(pdf_path)
        
        if 'error' not in info:
            try:
                # Add document type detection
                text = self.pdf_processor.extract_text_from_pdf(pdf_path)
                doc_type = self.detect_document_type(text)
                confidence = self.document_detector.get_detection_confidence(text)
                
                info.update({
                    'detected_type': doc_type,
                    'detection_confidence': confidence,
                    'text_length': len(text)
                })
            except Exception as e:
                info['detection_error'] = str(e)
        
        return info
    
    def _process_patterns_for_replacement(self, patterns: List[Tuple[str, str]], text: str) -> List[Tuple[str, str]]:
        """Process patterns to generate realistic replacements if needed."""
        replacement_mode = self.config.get("replacement_mode", "generic")
        
        if replacement_mode != "realistic" or not RealisticDataGenerator:
            return patterns
        
        # Create realistic data generator
        generator = RealisticDataGenerator(self.config)
        pattern_generators = get_pattern_generators()
        processed_patterns = []
        
        for pattern, replacement in patterns:
            if replacement.startswith("REALISTIC_"):
                # Extract category from replacement marker
                category = replacement.replace("REALISTIC_", "").lower()
                if category in pattern_generators:
                    # Generate realistic replacement dynamically
                    generator_method = getattr(generator, pattern_generators[category], None)
                    if generator_method:
                        # For now, generate a generic realistic value
                        # In practice, this would be done during actual redaction with matched text
                        realistic_replacement = generator_method()
                        processed_patterns.append((pattern, realistic_replacement))
                        continue
            
            # Keep original pattern if no realistic generation needed
            processed_patterns.append((pattern, replacement))
        
        return processed_patterns