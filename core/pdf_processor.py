"""
PDF processing utilities for document redaction.
"""
import fitz  # PyMuPDF
import re
import os
from typing import List, Tuple, Optional, Dict, Any

# Import realistic generators if available
try:
    from ..utils.realistic_generators import RealisticDataGenerator
    from ..config.patterns import get_pattern_generators, filter_balance_amounts, is_balance_amount
    from ..utils.nlp_name_detector import detect_names_nlp, detect_names_simple
    from ..utils.address_detector import detect_addresses_hybrid
except ImportError:
    try:
        from utils.realistic_generators import RealisticDataGenerator
        from config.patterns import get_pattern_generators, filter_balance_amounts, is_balance_amount
        from utils.nlp_name_detector import detect_names_nlp, detect_names_simple
        from utils.address_detector import detect_addresses_hybrid
    except ImportError:
        RealisticDataGenerator = None
        get_pattern_generators = None
        filter_balance_amounts = None
        is_balance_amount = None
        detect_names_nlp = None
        detect_names_simple = None
        detect_addresses_hybrid = None


class PDFProcessor:
    """Handles PDF-specific operations for redaction."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the PDF processor."""
        self.config = config or {}
        self.realistic_generator = None
        self.pattern_generators = None
        
        # Initialize realistic generators if needed
        if (self.config.get("replacement_mode") == "realistic" and 
            RealisticDataGenerator and get_pattern_generators):
            self.realistic_generator = RealisticDataGenerator(self.config)
            self.pattern_generators = get_pattern_generators()
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
            
        Raises:
            Exception: If PDF cannot be opened or read
        """
        try:
            doc = fitz.open(pdf_path)
            all_text = ""
            
            for page_num in range(len(doc)):
                all_text += doc[page_num].get_text("text") + " "
            
            doc.close()
            return all_text
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF {pdf_path}: {str(e)}")
    
    def redact_pdf_file(self, input_path: str, output_path: str, patterns: List[Tuple[str, str]]) -> bool:
        """
        Apply redaction patterns to a PDF file.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path for output redacted PDF
            patterns: List of (pattern, replacement) tuples
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.isfile(input_path):
                print(f"❌ File not found: {input_path}")
                return False

            doc = fitz.open(input_path)
            
            # Process each page
            for page_num in range(len(doc)):
                success = self._redact_page(doc[page_num], patterns)
                if not success:
                    print(f"⚠️  Warning: Issues redacting page {page_num + 1}")
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save the redacted document
            doc.save(output_path)
            doc.close()
            
            return True
            
        except Exception as e:
            print(f"❌ Error processing PDF: {str(e)}")
            if 'doc' in locals():
                doc.close()
            return False
    
    def _detect_names_with_enhanced_nlp(self, page) -> List[Tuple[str, str]]:
        """
        Enhanced two-phase name detection using multiple text extraction methods.

        Args:
            page: PyMuPDF page object

        Returns:
            List of (pattern, replacement) tuples for detected names
        """
        try:
            detected_names = set()

            # Phase 1: Extract names using multiple methods

            # Method 1: Default text format
            text_default = page.get_text()
            if detect_names_nlp:
                names_default = detect_names_nlp(text_default)
                for name, _, _ in names_default:
                    if len(name.strip()) > 2:
                        detected_names.add(name.strip())

            # Method 2: Blocks format with cleaned text
            blocks = page.get_text('blocks')
            text_blocks = ''
            for block in blocks:
                if len(block) >= 5 and isinstance(block[4], str):
                    # Clean block text, replace newlines with spaces
                    import re
                    cleaned_block = re.sub(r'\s+', ' ', block[4].strip())
                    text_blocks += cleaned_block + ' '

            if detect_names_nlp and text_blocks:
                names_blocks = detect_names_nlp(text_blocks)
                for name, _, _ in names_blocks:
                    if len(name.strip()) > 2:
                        detected_names.add(name.strip())

            # Method 3: Words format with adjacent word reconstruction
            words = page.get_text('words')
            for i, word in enumerate(words):
                if i < len(words) - 1:
                    current_word = word[4]
                    next_word = words[i + 1][4]
                    # Check for potential name combinations (adjacent capitalized words)
                    if (len(current_word) > 2 and len(next_word) > 2 and
                        current_word[0].isupper() and next_word[0].isupper() and
                        not any(char.isdigit() for char in current_word + next_word)):
                        combined = current_word + ' ' + next_word
                        detected_names.add(combined)

            # Phase 2: Generate replacement patterns
            name_patterns = []
            replacement_mode = self.config.get("replacement_mode", "generic")

            for name in detected_names:
                # Skip obvious non-names (containing numbers, special chars, etc.)
                if any(char.isdigit() for char in name) or len(name.split()) > 3:
                    continue

                # Create pattern for exact name matching
                escaped_name = re.escape(name)
                pattern = r'\b' + escaped_name + r'\b'

                # Generate appropriate replacement
                if replacement_mode == "realistic" and self.realistic_generator:
                    replacement = self.realistic_generator.generate_person_name(name)
                else:
                    replacement = "[FULL NAME]"

                name_patterns.append((pattern, replacement))

            return name_patterns

        except Exception as e:
            print(f"⚠️  Warning: Enhanced NLP name detection failed: {str(e)}")
            # Fallback to original method
            return self._detect_names_with_nlp(page.get_text())

    def _detect_names_with_nlp(self, text: str) -> List[Tuple[str, str]]:
        """
        Detect names using NLP and return as patterns for redaction.
        
        Args:
            text: Text to analyze for names
            
        Returns:
            List of (pattern, replacement) tuples for detected names
        """
        if not detect_names_nlp and not detect_names_simple:
            return []
        
        name_patterns = []
        
        try:
            # Try advanced NLP first
            if detect_names_nlp:
                names = detect_names_nlp(text)
            else:
                names = detect_names_simple(text)
            
            for name_text, start_pos, end_pos in names:
                # Create a literal pattern for the exact name found
                # Escape special regex characters
                escaped_name = re.escape(name_text)
                pattern = f"\\b{escaped_name}\\b"
                
                # Determine replacement based on current mode
                if self.config.get("replacement_mode") == "realistic" and self.realistic_generator:
                    replacement = self.realistic_generator.generate_person_name(name_text)
                elif self.config.get("replacement_mode") == "custom":
                    custom_replacements = self.config.get("replacement_settings", {}).get("custom_replacements", {})
                    replacement = custom_replacements.get("names", "[NAME]")
                else:
                    replacement = "[NAME]"
                
                name_patterns.append((pattern, replacement))
                
        except Exception as e:
            print(f"⚠️  Warning: NLP name detection failed: {str(e)}")
        
        return name_patterns

    def _detect_addresses_with_hybrid(self, text: str) -> List[Tuple[str, str]]:
        """
        Detect addresses using hybrid NLP+regex and return as patterns for redaction.
        
        Args:
            text: Text to analyze for addresses
            
        Returns:
            List of (pattern, replacement) tuples for detected addresses
        """
        if not detect_addresses_hybrid:
            return []
        
        address_patterns = []
        
        try:
            # Use hybrid address detection
            addresses = detect_addresses_hybrid(text)
            
            for address_text, start_pos, end_pos in addresses:
                # Create a flexible pattern that handles variable whitespace
                # Split address into words and escape each word separately
                words = address_text.split()
                escaped_words = [re.escape(word) for word in words]
                # Join with flexible whitespace pattern that matches 1 or more spaces
                pattern = r'\b' + r'\s+'.join(escaped_words) + r'\b'
                
                # Determine replacement based on current mode
                if self.config.get("replacement_mode") == "realistic" and self.realistic_generator:
                    replacement = self.realistic_generator.generate_address(address_text)
                elif self.config.get("replacement_mode") == "custom":
                    custom_replacements = self.config.get("replacement_settings", {}).get("custom_replacements", {})
                    replacement = custom_replacements.get("address", "[ADDRESS REDACTED]")
                else:
                    replacement = "[ADDRESS REDACTED]"
                
                address_patterns.append((pattern, replacement))
                
        except Exception as e:
            print(f"⚠️  Warning: Hybrid address detection failed: {str(e)}")
        
        return address_patterns

    def _redact_page(self, page, patterns: List[Tuple[str, str]]) -> bool:
        """
        Apply redaction patterns to a single PDF page.
        
        Args:
            page: PyMuPDF page object
            patterns: List of (pattern, replacement) tuples
            
        Returns:
            True if successful, False if there were issues
        """
        try:
            page_text = page.get_text("text")
            page_text_lower = page_text.lower()
            redaction_items = []
            
            # Add NLP-detected names to patterns if name redaction is enabled
            all_patterns = patterns.copy()
            if self.config.get("enabled_categories", {}).get("names", False):
                # Use enhanced two-phase name detection
                nlp_name_patterns = self._detect_names_with_enhanced_nlp(page)
                all_patterns.extend(nlp_name_patterns)
                if nlp_name_patterns:
                    print(f"🤖 NLP detected {len(nlp_name_patterns)} potential name(s) on this page")
            
            # Add hybrid-detected addresses to patterns if address redaction is enabled
            if self.config.get("enabled_categories", {}).get("address", False):
                hybrid_address_patterns = self._detect_addresses_with_hybrid(page_text)
                all_patterns.extend(hybrid_address_patterns)
                if hybrid_address_patterns:
                    print(f"🏠 Hybrid detected {len(hybrid_address_patterns)} potential address(es) on this page")
            
            # Collect all matches first for balance filtering
            all_matches = []
            custom_matches_found = 0

            for pattern, replacement in all_patterns:
                try:
                    matches = list(re.finditer(pattern, page_text, flags=re.IGNORECASE))

                    for match in matches:
                        matched_text = match.group()
                        start_pos = match.start()
                        end_pos = match.end()

                        # Determine pattern category (needed for balance filtering)
                        category = self._determine_pattern_category(pattern, replacement)

                        all_matches.append((matched_text, replacement, start_pos, end_pos, category))

                        if replacement == "[CUSTOM_REDACTED]":
                            custom_matches_found += 1

                except re.error as e:
                    print(f"⚠️  Invalid regex pattern '{pattern}': {str(e)}")
                    continue
                except Exception as e:
                    print(f"⚠️  Error processing pattern '{pattern}': {str(e)}")
                    continue

            if custom_matches_found > 0:
                print(f"🎯 Found {custom_matches_found} custom string match(es) on this page")

            # Apply balance filtering if available
            if filter_balance_amounts:
                filtered_matches = filter_balance_amounts(all_matches, page_text)
                print(f"🏦 Balance filtering: {len(all_matches)} → {len(filtered_matches)} matches (preserved {len(all_matches) - len(filtered_matches)} balance amounts)")
            else:
                filtered_matches = all_matches

            # Process filtered matches
            custom_redactions_processed = 0
            for matched_text, replacement, start_pos, end_pos, category in filtered_matches:
                try:
                    locations = page.search_for(matched_text)

                    # Generate realistic replacement if needed
                    final_replacement = self._resolve_replacement(replacement, matched_text)

                    for rect in locations:
                        # Adjust rectangle to prevent overlapping text issues
                        rect.x0 += 0.5  # left
                        rect.y0 += 2    # top
                        rect.x1 -= 0.5  # right
                        rect.y1 -= 2    # bottom

                        # Add redaction annotation
                        page.add_redact_annot(rect, text="", fill=(1, 1, 1))

                        # Store for replacement text insertion
                        redaction_items.append((rect, final_replacement))

                        if replacement == "[CUSTOM_REDACTED]":
                            custom_redactions_processed += 1
                
                except Exception as e:
                    print(f"⚠️  Error processing matched text '{matched_text}': {str(e)}")
                    continue

            if custom_redactions_processed > 0:
                print(f"🎯 Applied {custom_redactions_processed} custom string redaction(s) on this page")

            # Apply all redactions
            page.apply_redactions()

            # Insert replacement text
            self._insert_replacement_text(page, redaction_items)
            
            return True
            
        except Exception as e:
            print(f"⚠️  Error redacting page: {str(e)}")
            return False

    def _determine_pattern_category(self, pattern: str, replacement: str) -> str:
        """
        Determine the category of a pattern based on its replacement text.

        Args:
            pattern: The regex pattern
            replacement: The replacement text

        Returns:
            The category name (e.g., 'currency', 'ssn', 'phone', etc.)
        """
        # Map replacement patterns to categories
        if replacement in ['$X,XXX.XX', 'X,XXX.XX']:
            return 'currency'
        elif replacement in ['XXX-XX-XXXX']:
            return 'ssn'
        elif replacement in ['(XXX) XXX-XXXX', 'XXX-XXX-XXXX', '1-XXX-XXX-XXXX']:
            return 'phone'
        elif replacement in ['XXXX XXXX XXXX', 'XXXXXXXXXX', 'ACCOUNT XXXXXXXXXX', 'ACCOUNT XXXX XXXX XXXX']:
            return 'account_number'
        elif replacement in ['XXXXXXXXX']:
            return 'routing_number'
        elif replacement in ['XXXX-XXXX-XXXX-XXXX', 'XXXX-XXXXXX-XXXXX']:
            return 'credit_card'
        elif replacement in ['XX-XXXXXXX']:
            return 'tax_id'
        elif replacement in ['XX/XX/XXXX', 'Month XX, XXXX']:
            return 'dates'
        elif replacement in ['user@domain.com']:
            return 'email'
        elif replacement in ['[STREET ADDRESS]', '[CITY, STATE ZIP]', 'P.O. BOX [NUMBER]']:
            return 'address'
        elif replacement in ['Employer: [EMPLOYER NAME]', 'Company: [COMPANY NAME]']:
            return 'employer'
        elif replacement in ['[FULL NAME]']:
            return 'names'
        elif replacement in ['[REDACTED]', '[CUSTOM_REDACTED]']:
            return 'custom_strings'
        else:
            # Default category for unknown patterns
            return 'unknown'
    
    def _insert_replacement_text(self, page, redaction_items: List[Tuple[any, str]]):
        """
        Insert replacement text for redacted areas.
        
        Args:
            page: PyMuPDF page object
            redaction_items: List of (rect, replacement_text) tuples
        """
        # Remove overlapping redactions (keep larger ones)
        cleaned_items = self._remove_overlapping_redactions(redaction_items)
        
        # Insert replacement text
        for rect, replacement in cleaned_items:
            try:
                page.insert_htmlbox(
                    rect, 
                    replacement, 
                    css="* {font-family: sans-serif; font-size: 14px; color: black;}"
                )
            except Exception as e:
                print(f"⚠️  Warning: Could not insert replacement text '{replacement}': {str(e)}")
    
    def _remove_overlapping_redactions(self, redaction_items: List[Tuple[any, str]]) -> List[Tuple[any, str]]:
        """
        Remove overlapping redaction rectangles, keeping the larger ones.
        
        Args:
            redaction_items: List of (rect, replacement) tuples
            
        Returns:
            Cleaned list without overlaps
        """
        if not redaction_items:
            return []
        
        cleaned = []
        
        for rect, replacement in redaction_items:
            overlapping = False
            
            # Check against existing items
            for existing_rect, existing_replacement in cleaned:
                if rect.intersects(existing_rect):
                    # Keep the larger rectangle
                    if rect.get_area() <= existing_rect.get_area():
                        overlapping = True
                        break
                    else:
                        # Remove the smaller existing one
                        cleaned = [(r, rep) for r, rep in cleaned if not r.intersects(existing_rect)]
            
            if not overlapping:
                cleaned.append((rect, replacement))
        
        return cleaned
    
    def validate_pdf(self, pdf_path: str) -> tuple[bool, str]:
        """
        Validate that a file is a readable PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not os.path.exists(pdf_path):
                return False, f"File does not exist: {pdf_path}"
            
            if not pdf_path.lower().endswith('.pdf'):
                return False, f"File is not a PDF: {pdf_path}"
            
            # Try to open and read basic info
            doc = fitz.open(pdf_path)
            page_count = len(doc)
            doc.close()
            
            if page_count == 0:
                return False, f"PDF has no pages: {pdf_path}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Cannot read PDF {pdf_path}: {str(e)}"
    
    def get_pdf_info(self, pdf_path: str) -> dict:
        """
        Get basic information about a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF information
        """
        try:
            doc = fitz.open(pdf_path)
            info = {
                'page_count': len(doc),
                'metadata': doc.metadata,
                'is_encrypted': doc.is_encrypted,
                'file_size': os.path.getsize(pdf_path)
            }
            doc.close()
            return info
        except Exception as e:
            return {'error': str(e)}
    
    def _resolve_replacement(self, replacement: str, original_text: str) -> str:
        """Resolve replacement text, generating realistic values if needed."""
        if not replacement.startswith("REALISTIC_") or not self.realistic_generator:
            return replacement
        
        # Extract category from replacement marker
        category = replacement.replace("REALISTIC_", "").lower()
        
        if not self.pattern_generators or category not in self.pattern_generators:
            return replacement
        
        # Get the generator method
        generator_method_name = self.pattern_generators[category]
        generator_method = getattr(self.realistic_generator, generator_method_name, None)
        
        if generator_method:
            try:
                # Generate realistic replacement with original text as seed for consistency
                return generator_method(original_text)
            except Exception as e:
                print(f"⚠️  Warning: Could not generate realistic {category}: {str(e)}")
                return replacement
        
        return replacement