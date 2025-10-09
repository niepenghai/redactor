"""
Address Detection V2 - Clear pipeline architecture similar to name detection.

Pipeline:
1. Clean PDF text (remove newlines, etc.)
2. Extract candidate addresses using regex patterns
3. Validate candidates with spaCy NER
4. Parse addresses into structured components (street, city, state, zip)
5. Map back to original PDF text for replacement
"""

import re
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass

try:
    from .spacy_singleton import get_spacy_model
except ImportError:
    from spacy_singleton import get_spacy_model


@dataclass
class ParsedAddress:
    """Represents a parsed address with components."""
    full_address: str
    street: str
    city: str
    state: str
    zipcode: str
    confidence: float
    positions: List[Tuple[int, int]]  # List of (start, end) positions in original text


class AddressDetectorV2:
    """
    Address Detector V2 with clear pipeline:
    Text Cleaning → Pattern Extraction → spaCy Validation → Address Parsing → Replacement
    """

    def __init__(self):
        """Initialize the V2 address detector."""
        # Use singleton spaCy model
        self.nlp = get_spacy_model()

        # US state codes for validation
        self.us_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'
        }

        # Street type abbreviations
        self.street_types = {
            'Street', 'St', 'Avenue', 'Ave', 'Road', 'Rd', 'Drive', 'Dr',
            'Lane', 'Ln', 'Boulevard', 'Blvd', 'Way', 'Court', 'Ct',
            'Place', 'Pl', 'Circle', 'Cir', 'Parkway', 'Pkwy', 'Trail', 'Trl'
        }

    def detect_addresses_in_pdf(self, page, known_person_names: Optional[List[str]] = None) -> List[ParsedAddress]:
        """
        Main detection pipeline for a PDF page.

        Args:
            page: PyMuPDF page object
            known_person_names: Optional list of already-detected person names to exclude

        Returns:
            List of ParsedAddress objects with positions in original text
        """
        if known_person_names is None:
            known_person_names = []

        print(f"\n{'='*70}")
        print("📍 Starting Address Detection Pipeline V2")
        print(f"{'='*70}")

        if known_person_names:
            print(f"ℹ️  Will exclude {len(known_person_names)} known person name(s)")

        # Step 1: Extract and clean text from PDF
        print(f"\n{'─'*70}")
        print("STEP 1: Extract and Clean PDF Text")
        print(f"{'─'*70}")
        original_text = page.get_text()
        print(f"✓ Original text length: {len(original_text)} characters")
        print(f"✓ Original text preview (first 200 chars):")
        print(f"  {original_text[:200]!r}...")

        cleaned_text = self._clean_pdf_text(original_text)
        print(f"✓ Cleaned text length: {len(cleaned_text)} characters")
        print(f"✓ Cleaned text preview (first 200 chars):")
        print(f"  {cleaned_text[:200]!r}...")

        # Step 2: Extract candidate addresses using patterns
        print(f"\n{'─'*70}")
        print("STEP 2: Extract Candidate Addresses (Pattern Matching)")
        print(f"{'─'*70}")
        candidates = self._extract_candidates(cleaned_text)
        print(f"✓ Found {len(candidates)} candidate(s):")
        for i, candidate in enumerate(candidates, 1):
            print(f"  {i}. '{candidate}'")
        if not candidates:
            print("  (No candidates found)")

        # Step 2.5: Remove known person names from candidates
        if known_person_names:
            print(f"\n{'─'*70}")
            print("STEP 2.5: Filter Out Known Person Names from Candidates")
            print(f"{'─'*70}")
            filtered_candidates = []
            for candidate in candidates:
                cleaned = self._remove_known_names_from_address(candidate, known_person_names)
                if cleaned and len(cleaned) >= 5:
                    filtered_candidates.append(cleaned)
                    if cleaned != candidate:
                        print(f"  • '{candidate}' → '{cleaned}'")
                else:
                    print(f"  ⊘ Removed '{candidate}' (only contained person names)")
            candidates = filtered_candidates
            print(f"✓ {len(candidates)} candidate(s) after filtering")

        # Step 3: Validate candidates with spaCy
        print(f"\n{'─'*70}")
        print("STEP 3: Validate Candidates and Filter Person Names")
        print(f"{'─'*70}")
        validated_addresses = self._validate_with_spacy(candidates, cleaned_text, known_person_names)
        print(f"✓ Validated {len(validated_addresses)} address(es):")
        for i, (addr, confidence) in enumerate(validated_addresses, 1):
            print(f"  {i}. '{addr}' (confidence: {confidence:.2f})")
        if not validated_addresses:
            print("  (No addresses validated)")

        # Step 4: Parse addresses into components
        print(f"\n{'─'*70}")
        print("STEP 4: Parse Addresses into Components")
        print(f"{'─'*70}")
        parsed_addresses = self._parse_address_components(validated_addresses)
        print(f"✓ Parsed {len(parsed_addresses)} address(es):")
        for i, addr_info in enumerate(parsed_addresses, 1):
            print(f"  {i}. Full: '{addr_info['full_address']}'")
            print(f"     - Street: '{addr_info['street']}'")
            print(f"     - City: '{addr_info['city']}'")
            print(f"     - State: '{addr_info['state']}'")
            print(f"     - Zipcode: '{addr_info['zipcode']}'")
            print(f"     - Confidence: {addr_info['confidence']:.2f}")

        # Step 5: Convert to final ParsedAddress objects
        print(f"\n{'─'*70}")
        print("STEP 5: Finalize Parsed Addresses")
        print(f"{'─'*70}")
        final_addresses = self._map_to_original_text(parsed_addresses, original_text)
        print(f"✓ Finalized {len(final_addresses)} address(es):")
        for i, parsed_addr in enumerate(final_addresses, 1):
            print(f"  {i}. '{parsed_addr.full_address}'")
            print(f"     - Components: {parsed_addr.street} | {parsed_addr.city} | {parsed_addr.state} | {parsed_addr.zipcode}")
            print(f"     - Confidence: {parsed_addr.confidence:.2f}")

        print(f"\n{'='*70}")
        print(f"✅ Pipeline Complete: {len(final_addresses)} address(es) detected")
        print(f"{'='*70}\n")

        return final_addresses

    def _clean_pdf_text(self, text: str) -> str:
        """
        Clean PDF text for better address detection.

        NOTE: Keep newlines for now - they help as boundaries between different text blocks.
        We'll normalize spaces within lines.

        Args:
            text: Raw PDF text

        Returns:
            Cleaned text (with newlines preserved)
        """
        # Normalize multiple spaces to single space within each line
        # but keep newlines as-is for boundary detection
        lines = text.split('\n')
        cleaned_lines = [re.sub(r'[ \t]+', ' ', line.strip()) for line in lines]
        cleaned = '\n'.join(cleaned_lines)

        return cleaned

    def _extract_candidates(self, text: str) -> List[str]:
        """
        Extract candidate addresses using regex patterns.

        Args:
            text: Cleaned text

        Returns:
            List of candidate address strings
        """
        candidates = []

        # Pattern 1: Street address (number + street name + type)
        street_pattern = r'\b\d+\s+[A-Z][A-Za-z0-9\s]*?\s+(?:' + '|'.join(self.street_types) + r')\b(?:\s+(?:Suite|Ste|Apt|Apartment|Unit|#)\s*[A-Za-z0-9-]+)?'
        matches = re.finditer(street_pattern, text, re.IGNORECASE)
        for match in matches:
            candidate = match.group().strip()
            if len(candidate) > 5:  # Minimum length check
                candidates.append(candidate)

        # Pattern 2: P.O. Box
        po_box_pattern = r'\bP\.?\s*O\.?\s*Box\s+\d+\b'
        matches = re.finditer(po_box_pattern, text, re.IGNORECASE)
        for match in matches:
            candidates.append(match.group().strip())

        # Pattern 3: City, State ZIP (with comma)
        city_state_comma_pattern = r'\b[A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b'
        matches = re.finditer(city_state_comma_pattern, text)
        for match in matches:
            candidates.append(match.group().strip())

        # Pattern 4: CITY STATE ZIP (all caps, no comma)
        # Strategy: Find STATE + ZIP first, then look backwards for city name only ON THE SAME LINE
        state_zip_pattern = r'\b([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\b'

        for match in re.finditer(state_zip_pattern, text):
            state_code = match.group(1)
            zipcode = match.group(2)

            # Validate state code
            if state_code not in self.us_states:
                continue

            # Find the start and end positions of the match
            match_start = match.start()
            match_end = match.end()

            # Find the line containing this STATE ZIP
            # Look backwards from match_start to find the start of this line
            line_start = text.rfind('\n', 0, match_start) + 1  # +1 to skip the newline itself

            # Look forwards from match_end to find the end of this line
            line_end_pos = text.find('\n', match_end)
            if line_end_pos == -1:
                line_end_pos = len(text)

            # Extract only the current line
            current_line = text[line_start:line_end_pos].strip()

            # Find where the STATE ZIP pattern appears in this line
            # Use word boundary to avoid matching "CA" in "CASTRO"
            state_zip_in_line = re.search(r'\b' + re.escape(state_code) + r'\s+' + re.escape(zipcode) + r'\b', current_line)
            if not state_zip_in_line:
                continue

            # Get text before state code on THIS LINE ONLY
            text_before_state = current_line[:state_zip_in_line.start()].rstrip()

            # Extract city - take last 1-3 all-caps words before state
            city_words = []
            words_before = text_before_state.split()

            for word in reversed(words_before):
                # Stop if we hit non-city-like words
                if not word.isupper() or len(word) < 2:
                    break

                # Skip common non-address words
                if word in {'ADDRESS', 'SERVICE', 'REQUESTED', 'STATEMENT', 'ACCOUNT',
                           'BALANCE', 'TOTAL', 'AMOUNT', 'PAYMENT', 'DUE', 'DATE',
                           'DESCRIPTION', 'TRANSACTION', 'SUMMARY', 'DETAILS', 'FROM',
                           'TO', 'ATTN', 'ATTENTION', 'FOR', 'RE', 'REF'}:
                    break

                city_words.insert(0, word)

                # Limit to 3 words for city name (e.g., "SAN JOSE HILLS")
                if len(city_words) >= 3:
                    break

            # Must have at least one city word
            if city_words:
                full_address = f"{' '.join(city_words)} {state_code} {zipcode}"
                candidates.append(full_address)

        # Remove duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                unique_candidates.append(candidate)

        return unique_candidates

    def _validate_with_spacy(self, candidates: List[str], context: str, known_person_names: List[str]) -> List[Tuple[str, float]]:
        """
        Validate address candidates using spaCy NER and filter out person names.

        Args:
            candidates: List of candidate address strings
            context: Full text context
            known_person_names: List of known person names to exclude

        Returns:
            List of (address, confidence) tuples for validated addresses
        """
        validated = []

        for candidate in candidates:
            # Remove known person names from candidate
            cleaned_candidate = self._remove_known_names_from_address(candidate, known_person_names)

            # Also try spaCy-based person name removal (for mixed case names)
            if self.nlp:
                cleaned_candidate = self._remove_person_names_from_address(cleaned_candidate)

            # Skip if nothing left after removing names
            if not cleaned_candidate or len(cleaned_candidate) < 5:
                print(f"    ⊘ Skipped '{candidate}' (only person names)")
                continue

            # Rule-based confidence (without NLP for structure validation)
            confidence = self._calculate_address_confidence(cleaned_candidate, context)

            # Only accept if confidence is high enough
            if confidence >= 0.6:
                validated.append((cleaned_candidate, confidence))
            else:
                print(f"    ⊘ Skipped '{cleaned_candidate}' (low confidence: {confidence:.2f})")

        return validated

    def _remove_known_names_from_address(self, address: str, known_names: List[str]) -> str:
        """
        Remove known person names from address string.

        Args:
            address: Address candidate
            known_names: List of known person names

        Returns:
            Address with known names removed
        """
        if not known_names:
            return address

        cleaned = address

        for name in known_names:
            # Try exact match (case-insensitive)
            if name.upper() in cleaned.upper():
                # Replace the name with empty string
                # Use word boundaries to avoid partial matches
                pattern = re.escape(name)
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    def _remove_person_names_from_address(self, address: str) -> str:
        """
        Remove person names from address string using spaCy NER.

        Args:
            address: Address candidate that may contain person names

        Returns:
            Address with person names removed
        """
        if not self.nlp:
            return address

        doc = self.nlp(address)

        # Find PERSON entities
        person_spans = [(ent.start_char, ent.end_char) for ent in doc.ents if ent.label_ == "PERSON"]

        if not person_spans:
            return address

        # Remove person names from the address
        # Work backwards to preserve indices
        cleaned = address
        for start, end in sorted(person_spans, reverse=True):
            cleaned = cleaned[:start] + cleaned[end:]

        # Clean up extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        return cleaned

    def _calculate_address_confidence(self, address: str, context: str) -> float:
        """
        Calculate confidence score for an address candidate.

        Args:
            address: Address candidate
            context: Surrounding text context

        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.5  # Base confidence

        # Check for numbers (addresses should have numbers)
        if re.search(r'\d', address):
            confidence += 0.2

        # Check for state code
        words = address.split()
        if any(word in self.us_states for word in words):
            confidence += 0.2

        # Check for zip code
        if re.search(r'\b\d{5}(-\d{4})?\b', address):
            confidence += 0.15

        # Check for street type
        if any(st_type in address for st_type in self.street_types):
            confidence += 0.15

        # Check context for address-related terms
        address_context_terms = ['address', 'mail', 'send', 'located', 'at', 'street']
        if any(term in context.lower() for term in address_context_terms):
            confidence += 0.1

        # Reduce confidence if it looks like business name only
        business_terms = ['bank', 'corp', 'company', 'inc', 'llc']
        if any(term in address.lower() for term in business_terms):
            confidence -= 0.2

        # Reduce confidence if it contains financial terms
        financial_terms = ['balance', 'total', 'amount', 'account', 'payment']
        if any(term in address.lower() for term in financial_terms):
            confidence -= 0.3

        return max(0.0, min(1.0, confidence))

    def _parse_address_components(self, validated_addresses: List[Tuple[str, float]]) -> List[dict]:
        """
        Parse addresses into structured components.

        Args:
            validated_addresses: List of (address, confidence) tuples

        Returns:
            List of dictionaries with parsed address components
        """
        parsed = []

        for address, confidence in validated_addresses:
            components = {
                'full_address': address,
                'street': '',
                'city': '',
                'state': '',
                'zipcode': '',
                'confidence': confidence
            }

            # Extract zipcode
            zip_match = re.search(r'\b(\d{5}(?:-\d{4})?)\b', address)
            if zip_match:
                components['zipcode'] = zip_match.group(1)

            # Extract state (2-letter code before zipcode)
            state_match = re.search(r'\b([A-Z]{2})\s+\d{5}', address)
            if state_match and state_match.group(1) in self.us_states:
                components['state'] = state_match.group(1)

            # Extract city (text before state)
            if components['state']:
                # Find text before state code using word boundary to avoid matching "CA" in "CASTRO"
                state_pattern = r'\b' + re.escape(components['state']) + r'\b'
                state_match = re.search(state_pattern, address)
                if not state_match:
                    # Fallback to simple find if regex fails
                    state_pos = address.find(components['state'])
                else:
                    state_pos = state_match.start()
                before_state = address[:state_pos].strip()

                # Remove street address if present
                # Check for street types
                street_found = False
                for st_type in self.street_types:
                    if st_type in before_state:
                        st_type_pos = before_state.rfind(st_type)
                        # Street is everything up to and including street type
                        components['street'] = before_state[:st_type_pos + len(st_type)].strip()
                        # City is everything after street type
                        after_street = before_state[st_type_pos + len(st_type):].strip()
                        # Remove leading comma if present
                        after_street = re.sub(r'^,\s*', '', after_street)
                        components['city'] = after_street.strip()
                        street_found = True
                        break

                if not street_found:
                    # No street found, everything before state is city
                    # Remove trailing comma if present
                    components['city'] = re.sub(r',\s*$', '', before_state).strip()

            # Special case: P.O. Box
            if 'P.O. Box' in address or 'PO Box' in address:
                components['street'] = re.search(r'P\.?\s*O\.?\s*Box\s+\d+', address, re.IGNORECASE).group()

            # If we only have a street address, mark it as street only
            if not components['city'] and not components['state'] and not components['zipcode']:
                components['street'] = address

            parsed.append(components)

        return parsed

    def _map_to_original_text(self, parsed_addresses: List[dict], original_text: str) -> List[ParsedAddress]:
        """
        Convert parsed address dictionaries to ParsedAddress objects.

        Note: We don't calculate text positions here. The actual PDF coordinates
        will be found later using page.search_for() in the PDF processor.

        Args:
            parsed_addresses: List of parsed address dictionaries
            original_text: Original PDF text (not used, but kept for compatibility)

        Returns:
            List of ParsedAddress objects
        """
        final_addresses = []

        for addr_info in parsed_addresses:
            # Simply convert dict to ParsedAddress object
            # No need to find positions in text - page.search_for() will do that in PDF
            final_addresses.append(ParsedAddress(
                full_address=addr_info['full_address'],
                street=addr_info['street'],
                city=addr_info['city'],
                state=addr_info['state'],
                zipcode=addr_info['zipcode'],
                confidence=addr_info['confidence'],
                positions=[]  # Will be filled by page.search_for() in PDF processor
            ))

        return final_addresses


# Convenience function for integration
def detect_addresses_v2(page) -> List[ParsedAddress]:
    """
    Detect addresses in a PDF page using the v2 pipeline.

    Args:
        page: PyMuPDF page object

    Returns:
        List of ParsedAddress objects
    """
    detector = AddressDetectorV2()
    return detector.detect_addresses_in_pdf(page)
