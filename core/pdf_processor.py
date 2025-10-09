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
    from ..utils.name_detector_v2 import NameDetectorV2
    from ..utils.address_detector_v2 import AddressDetectorV2
except ImportError:
    try:
        from utils.realistic_generators import RealisticDataGenerator
        from config.patterns import get_pattern_generators, filter_balance_amounts, is_balance_amount
        from utils.nlp_name_detector import detect_names_nlp, detect_names_simple
        from utils.address_detector import detect_addresses_hybrid
        from utils.name_detector_v2 import NameDetectorV2
        from utils.address_detector_v2 import AddressDetectorV2
    except ImportError:
        RealisticDataGenerator = None
        get_pattern_generators = None
        filter_balance_amounts = None
        is_balance_amount = None
        detect_names_nlp = None
        detect_names_simple = None
        detect_addresses_hybrid = None
        NameDetectorV2 = None
        AddressDetectorV2 = None


class PDFProcessor:
    """Handles PDF-specific operations for redaction."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the PDF processor."""
        self.config = config or {}
        self.realistic_generator = None
        self.pattern_generators = None
        self.name_detector_v2 = None
        self.address_detector_v2 = None

        # Initialize realistic generators if needed
        if (self.config.get("replacement_mode") == "realistic" and
            RealisticDataGenerator and get_pattern_generators):
            self.realistic_generator = RealisticDataGenerator(self.config)
            self.pattern_generators = get_pattern_generators()

        # Initialize name detector v2 if available
        if NameDetectorV2:
            self.name_detector_v2 = NameDetectorV2()

        # Initialize address detector v2 if available
        if AddressDetectorV2:
            self.address_detector_v2 = AddressDetectorV2()
    
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
            total_pages = len(doc)

            print(f"\n{'='*80}")
            print(f"📄 Processing PDF: {os.path.basename(input_path)}")
            print(f"   Total pages: {total_pages}")
            print(f"{'='*80}")

            # Process each page
            for page_num in range(total_pages):
                print(f"\n{'#'*80}")
                print(f"📃 Processing Page {page_num + 1} of {total_pages}")
                print(f"{'#'*80}")

                success = self._redact_page(doc[page_num], patterns)

                if not success:
                    print(f"⚠️  Warning: Issues redacting page {page_num + 1}")
                else:
                    print(f"\n✅ Page {page_num + 1} completed successfully")

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Save the redacted document
            print(f"\n{'='*80}")
            print(f"💾 Saving redacted PDF...")
            print(f"   Output: {os.path.basename(output_path)}")
            print(f"{'='*80}")

            doc.save(output_path)
            doc.close()

            print(f"\n{'='*80}")
            print(f"✅ PDF Processing Complete!")
            print(f"   Input:  {os.path.basename(input_path)}")
            print(f"   Output: {os.path.basename(output_path)}")
            print(f"   Pages:  {total_pages}")
            print(f"{'='*80}\n")

            return True
            
        except Exception as e:
            print(f"❌ Error processing PDF: {str(e)}")
            if 'doc' in locals():
                doc.close()
            return False
    
    def _detect_names_with_enhanced_nlp(self, page) -> Tuple[List[Tuple[str, str]], List[str]]:
        """
        Enhanced name detection using the V2 pipeline.

        Args:
            page: PyMuPDF page object

        Returns:
            Tuple of:
            - List of (pattern, replacement) tuples for detected names
            - List of detected person name strings (full names + components)
        """
        try:
            # Use V2 detector if available
            if self.name_detector_v2:
                print("\n🔍 Using Name Detector V2 pipeline...")
                parsed_names = self.name_detector_v2.detect_names_in_pdf(page)

                # Convert ParsedName objects to (pattern, replacement) tuples
                name_patterns = []
                person_name_list = []  # Track all name components
                replacement_mode = self.config.get("replacement_mode", "generic")

                for parsed_name in parsed_names:
                    # Create pattern for exact name matching
                    escaped_name = re.escape(parsed_name.full_name)
                    pattern = r'\b' + escaped_name + r'\b'

                    # Generate appropriate replacement
                    if replacement_mode == "realistic" and self.realistic_generator:
                        replacement = self.realistic_generator.generate_person_name(parsed_name.full_name)
                    else:
                        replacement = "[FULL NAME]"

                    name_patterns.append((pattern, replacement))

                    # Collect all name components for address filtering
                    person_name_list.append(parsed_name.full_name)
                    if parsed_name.first_name:
                        person_name_list.append(parsed_name.first_name)
                    if parsed_name.middle_name:
                        person_name_list.append(parsed_name.middle_name)
                    if parsed_name.last_name:
                        person_name_list.append(parsed_name.last_name)

                print(f"✅ V2 detector found {len(name_patterns)} name(s) for replacement\n")
                return name_patterns, person_name_list

            # Fallback to old method if V2 not available
            print("⚠️  V2 detector not available, using legacy method")
            detected_names = set()

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
                    if (len(current_word) > 2 and len(next_word) > 2 and
                        current_word[0].isupper() and next_word[0].isupper() and
                        not any(char.isdigit() for char in current_word + next_word)):
                        combined = current_word + ' ' + next_word
                        detected_names.add(combined)

            # Generate replacement patterns
            name_patterns = []
            person_name_list = list(detected_names)  # Use detected names as-is for legacy method
            replacement_mode = self.config.get("replacement_mode", "generic")

            for name in detected_names:
                if any(char.isdigit() for char in name) or len(name.split()) > 3:
                    continue

                escaped_name = re.escape(name)
                pattern = r'\b' + escaped_name + r'\b'

                if replacement_mode == "realistic" and self.realistic_generator:
                    replacement = self.realistic_generator.generate_person_name(name)
                else:
                    replacement = "[FULL NAME]"

                name_patterns.append((pattern, replacement))

            return name_patterns, person_name_list

        except Exception as e:
            print(f"⚠️  Warning: Enhanced NLP name detection failed: {str(e)}")
            fallback_patterns = self._detect_names_with_nlp(page.get_text())
            return fallback_patterns, []

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

    def _detect_addresses_with_v2(self, page, known_person_names: List[str] = None) -> List[Tuple[str, str]]:
        """
        Detect addresses using the V2 pipeline with structured parsing.

        Args:
            page: PyMuPDF page object
            known_person_names: List of known person names to exclude from addresses

        Returns:
            List of (pattern, replacement) tuples for detected addresses
        """
        try:
            if not self.address_detector_v2:
                return []

            if known_person_names is None:
                known_person_names = []

            print("\n🔍 Using Address Detector V2 pipeline...")
            parsed_addresses = self.address_detector_v2.detect_addresses_in_pdf(page, known_person_names)

            # Convert ParsedAddress objects to (pattern, replacement) tuples
            address_patterns = []
            replacement_mode = self.config.get("replacement_mode", "generic")

            for parsed_addr in parsed_addresses:
                # Create pattern for exact address matching
                escaped_address = re.escape(parsed_addr.full_address)
                pattern = r'\b' + escaped_address + r'\b'

                # Generate appropriate replacement based on mode
                if replacement_mode == "realistic" and self.realistic_generator:
                    replacement = self.realistic_generator.generate_address(parsed_addr.full_address)
                elif replacement_mode == "custom":
                    custom_replacements = self.config.get("replacement_settings", {}).get("custom_replacements", {})
                    replacement = custom_replacements.get("address", "[ADDRESS REDACTED]")
                else:
                    # Generic mode - use structured components if available
                    if parsed_addr.zipcode:
                        # Full address with city, state, zip
                        replacement = f"[CITY, {parsed_addr.state} {parsed_addr.zipcode}]"
                    elif parsed_addr.street:
                        # Just street address
                        replacement = "[STREET ADDRESS]"
                    else:
                        # Fallback
                        replacement = "[ADDRESS]"

                address_patterns.append((pattern, replacement))

            print(f"✅ V2 detector found {len(address_patterns)} address(es) for replacement\n")
            return address_patterns

        except Exception as e:
            print(f"⚠️  Warning: V2 address detection failed: {str(e)}")
            return []

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
            detected_person_names = []  # Track detected names for address filtering
            v2_detected_patterns = []  # Track V2-detected patterns (names + addresses)

            if self.config.get("enabled_categories", {}).get("names", False):
                # Use enhanced two-phase name detection
                nlp_name_patterns, detected_person_names = self._detect_names_with_enhanced_nlp(page)
                v2_detected_patterns.extend(nlp_name_patterns)
                all_patterns.extend(nlp_name_patterns)
                if nlp_name_patterns:
                    print(f"🤖 NLP detected {len(nlp_name_patterns)} potential name(s) on this page")

            # Add detected addresses to patterns if address redaction is enabled
            if self.config.get("enabled_categories", {}).get("address", False):
                if self.address_detector_v2:
                    # Use V2 detector with known person names
                    address_patterns = self._detect_addresses_with_v2(page, detected_person_names)
                    v2_detected_patterns.extend(address_patterns)
                    all_patterns.extend(address_patterns)
                    if address_patterns:
                        print(f"🏠 V2 detected {len(address_patterns)} potential address(es) on this page")
                else:
                    # Fallback to hybrid method
                    hybrid_address_patterns = self._detect_addresses_with_hybrid(page_text)
                    all_patterns.extend(hybrid_address_patterns)
                    if hybrid_address_patterns:
                        print(f"🏠 Hybrid detected {len(hybrid_address_patterns)} potential address(es) on this page")

            # Create masked text: replace V2-detected content with placeholders
            # This prevents generic patterns from matching already-detected content
            masked_text = page_text
            mask_map = []  # Track (start, end, original_text, placeholder) for restoration

            if v2_detected_patterns:
                print(f"\n{'─'*70}")
                print("STEP: Masking V2-Detected Content")
                print(f"{'─'*70}")

                # Find all V2 matches and their positions
                v2_matches = []
                for pattern, replacement in v2_detected_patterns:
                    for match in re.finditer(pattern, page_text, flags=re.IGNORECASE):
                        v2_matches.append((match.start(), match.end(), match.group()))

                # Sort by position (reverse order for replacement)
                v2_matches.sort(key=lambda x: x[0], reverse=True)

                # Replace from end to start to preserve positions
                for start, end, original in v2_matches:
                    placeholder = f"__V2_DETECTED_{len(mask_map)}__"
                    mask_map.append((start, end, original, placeholder))
                    masked_text = masked_text[:start] + placeholder + masked_text[end:]

                print(f"✓ Masked {len(mask_map)} V2-detected item(s)")

            # Collect all matches first for balance filtering
            print(f"\n{'─'*70}")
            print("STEP: Matching Patterns in Page Text")
            print(f"{'─'*70}")
            print(f"Total patterns to match: {len(all_patterns)}")

            all_matches = []
            custom_matches_found = 0

            for i, (pattern, replacement) in enumerate(all_patterns, 1):
                try:
                    # For V2 patterns, match against original text
                    # For generic patterns, match against masked text
                    is_v2_pattern = (pattern, replacement) in v2_detected_patterns
                    search_text = page_text if is_v2_pattern else masked_text

                    matches = list(re.finditer(pattern, search_text, flags=re.IGNORECASE))

                    if matches:
                        print(f"\nPattern {i}: {pattern[:50]}... → '{replacement}'")
                        print(f"  Found {len(matches)} match(es):")

                    for match in matches:
                        matched_text = match.group()
                        start_pos = match.start()
                        end_pos = match.end()

                        # Skip if this is a placeholder (for generic patterns)
                        if not is_v2_pattern and matched_text.startswith("__V2_DETECTED_"):
                            continue

                        print(f"    • '{matched_text}' at position [{start_pos}:{end_pos}]")

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

            print(f"\n✓ Total matches found: {len(all_matches)}")
            if custom_matches_found > 0:
                print(f"🎯 Found {custom_matches_found} custom string match(es) on this page")

            # Apply balance filtering if available
            if filter_balance_amounts:
                filtered_matches = filter_balance_amounts(all_matches, page_text)
                print(f"🏦 Balance filtering: {len(all_matches)} → {len(filtered_matches)} matches (preserved {len(all_matches) - len(filtered_matches)} balance amounts)")
            else:
                filtered_matches = all_matches

            # Process filtered matches
            print(f"\n{'─'*70}")
            print("STEP: Finding PDF Coordinates and Applying Redactions")
            print(f"{'─'*70}")

            custom_redactions_processed = 0
            for matched_text, replacement, start_pos, end_pos, category in filtered_matches:
                try:
                    locations = page.search_for(matched_text)

                    print(f"\n• Processing: '{matched_text}' → '{replacement}'")
                    print(f"  Category: {category}")
                    print(f"  PDF locations found: {len(locations)}")

                    # Generate realistic replacement if needed
                    final_replacement = self._resolve_replacement(replacement, matched_text)

                    for idx, rect in enumerate(locations, 1):
                        print(f"    Location {idx}: Rect({rect.x0:.1f}, {rect.y0:.1f}, {rect.x1:.1f}, {rect.y1:.1f})")

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

            print(f"\n✓ Total redaction items: {len(redaction_items)}")
            if custom_redactions_processed > 0:
                print(f"🎯 Applied {custom_redactions_processed} custom string redaction(s) on this page")

            # Apply all redactions
            print(f"\n{'─'*70}")
            print("STEP: Applying Redactions (deleting original text)")
            print(f"{'─'*70}")
            page.apply_redactions()
            print("✓ All redactions applied")

            # Insert replacement text
            print(f"\n{'─'*70}")
            print("STEP: Inserting Replacement Text")
            print(f"{'─'*70}")
            self._insert_replacement_text(page, redaction_items)
            print("✓ All replacement text inserted")
            
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
        print(f"Cleaning overlapping redactions: {len(redaction_items)} items")
        cleaned_items = self._remove_overlapping_redactions(redaction_items)
        print(f"After cleanup: {len(cleaned_items)} items")

        # Insert replacement text
        for idx, (rect, replacement) in enumerate(cleaned_items, 1):
            try:
                print(f"  {idx}. Inserting '{replacement}' at Rect({rect.x0:.1f}, {rect.y0:.1f}, {rect.x1:.1f}, {rect.y1:.1f})")
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