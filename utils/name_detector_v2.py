"""
Name Detection V2 - Clear pipeline architecture with detailed logging.

Flow:
1. Clean PDF text (remove newlines, normalize)
2. Use patterns to extract candidate names
3. Use spaCy to validate if they are real person names
4. Parse names into first/middle/last components
5. Replace in original PDF text
"""

import re
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass

try:
    from .spacy_singleton import get_spacy_model
except ImportError:
    from spacy_singleton import get_spacy_model


@dataclass
class ParsedName:
    """Represents a parsed name with components."""
    full_name: str
    first_name: str
    middle_name: str
    last_name: str
    confidence: float
    positions: List[Tuple[int, int]]  # List of (start, end) positions in original text


class NameDetectorV2:
    """
    Name Detector V2 with clear pipeline:
    Text Cleaning → Pattern Extraction → spaCy Validation → Name Parsing → Replacement
    """

    def __init__(self):
        """Initialize the detector with patterns and spaCy."""
        self.name_patterns = self._compile_name_patterns()
        self.financial_terms = self._load_financial_terms()
        # Use singleton spaCy model
        self.nlp = get_spacy_model()

    def _compile_name_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns for potential name extraction."""
        patterns = [
            # Title + Name patterns (highest priority)
            r'\b(?:Mr|Mrs|Ms|Dr|Prof|Rev)\.?\s+[A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+\b',

            # Standard formats
            r'\b[A-Z][a-z]{2,}\s+[A-Z]\.\s+[A-Z][a-z]{2,}\b',  # First M. Last
            r'\b[A-Z][a-z]{2,}\s+[A-Z]\s+[A-Z][a-z]{2,}\b',    # First M Last
            r'\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b',            # First Last

            # All caps formats (common in financial docs)
            r'\b[A-Z]{3,}\s+[A-Z]\.\s+[A-Z]{3,}\b',            # FIRST M. LAST
            r'\b[A-Z]{3,}\s+[A-Z]\s+[A-Z]{3,}\b',              # FIRST M LAST
            r'\b[A-Z]{3,}\s+[A-Z]{3,}\b',                      # FIRST LAST

            # Three-word names
            r'\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b',  # First Middle Last
        ]
        return [re.compile(p) for p in patterns]

    def _load_financial_terms(self) -> Set[str]:
        """Load financial/business terms to filter out."""
        return {
            # Financial terms
            'gross', 'pay', 'net', 'wage', 'salary', 'income', 'earnings',
            'total', 'amount', 'balance', 'deduction', 'tax', 'withholding',
            'rate', 'hours', 'overtime', 'regular', 'current', 'year',
            'date', 'period', 'check', 'deposit', 'withdrawal',

            # Business terms
            'account', 'number', 'summary', 'statement', 'service',
            'customer', 'banking', 'online', 'mobile', 'direct',

            # Address terms
            'street', 'avenue', 'road', 'drive', 'lane', 'main',

            # Common business names
            'bank', 'corp', 'company', 'inc', 'llc', 'wells', 'fargo'
        }

    def detect_names_in_pdf(self, page) -> List[ParsedName]:
        """
        Main detection pipeline for a PDF page.

        Args:
            page: PyMuPDF page object

        Returns:
            List of ParsedName objects with positions in original text
        """
        print(f"\n{'='*70}")
        print("📄 Starting Name Detection Pipeline")
        print(f"{'='*70}")

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

        # Step 2: Extract candidate names using patterns
        print(f"\n{'─'*70}")
        print("STEP 2: Extract Candidate Names (Pattern Matching)")
        print(f"{'─'*70}")
        candidates = self._extract_candidates(cleaned_text)
        print(f"✓ Found {len(candidates)} candidate(s):")
        for i, candidate in enumerate(candidates, 1):
            print(f"  {i}. '{candidate}'")
        if not candidates:
            print("  (No candidates found)")

        # Step 3: Validate candidates with spaCy
        print(f"\n{'─'*70}")
        print("STEP 3: Validate Candidates with spaCy")
        print(f"{'─'*70}")
        validated_names = self._validate_with_spacy(candidates, cleaned_text)
        print(f"✓ Validated {len(validated_names)} name(s):")
        for i, (name, confidence) in enumerate(validated_names, 1):
            print(f"  {i}. '{name}' (confidence: {confidence:.2f})")
        if not validated_names:
            print("  (No names validated)")

        # Step 4: Parse names into components
        print(f"\n{'─'*70}")
        print("STEP 4: Parse Names into Components")
        print(f"{'─'*70}")
        parsed_names = self._parse_name_components(validated_names)
        print(f"✓ Parsed {len(parsed_names)} name(s):")
        for i, name_info in enumerate(parsed_names, 1):
            print(f"  {i}. Full: '{name_info['full_name']}'")
            print(f"     - First: '{name_info['first_name']}'")
            print(f"     - Middle: '{name_info['middle_name']}'")
            print(f"     - Last: '{name_info['last_name']}'")
            print(f"     - Confidence: {name_info['confidence']:.2f}")

        # Step 5: Find positions in original text
        print(f"\n{'─'*70}")
        print("STEP 5: Map Names to Original PDF Text Positions")
        print(f"{'─'*70}")
        final_names = self._map_to_original_text(parsed_names, original_text)
        print(f"✓ Mapped {len(final_names)} name(s) to original text:")
        for i, parsed_name in enumerate(final_names, 1):
            print(f"  {i}. '{parsed_name.full_name}'")
            print(f"     - Components: {parsed_name.first_name} / {parsed_name.middle_name} / {parsed_name.last_name}")
            print(f"     - Positions: {len(parsed_name.positions)} occurrence(s)")
            for j, (start, end) in enumerate(parsed_name.positions, 1):
                print(f"       {j}) [{start}:{end}]")

        print(f"\n{'='*70}")
        print(f"✅ Pipeline Complete: {len(final_names)} name(s) detected")
        print(f"{'='*70}\n")

        return final_names

    def _clean_pdf_text(self, text: str) -> str:
        """
        Clean PDF text for better name detection.

        Args:
            text: Raw PDF text

        Returns:
            Cleaned text with normalized whitespace
        """
        # Replace multiple newlines with single space
        cleaned = re.sub(r'\n+', ' ', text)

        # Replace multiple spaces with single space
        cleaned = re.sub(r'\s+', ' ', cleaned)

        # Remove extra whitespace
        cleaned = cleaned.strip()

        return cleaned

    def _extract_candidates(self, text: str) -> List[str]:
        """
        Extract candidate names using regex patterns.

        Args:
            text: Cleaned text

        Returns:
            List of unique candidate name strings
        """
        candidates = set()

        for pattern in self.name_patterns:
            matches = pattern.findall(text)
            candidates.update(matches)

        # Filter out obvious non-names
        filtered_candidates = []
        for candidate in candidates:
            if self._is_valid_candidate(candidate):
                filtered_candidates.append(candidate)

        return filtered_candidates

    def _is_valid_candidate(self, candidate: str) -> bool:
        """
        Quick filter for obvious non-names.

        Args:
            candidate: Candidate name string

        Returns:
            True if candidate might be a name
        """
        # Check each word for financial terms
        words = candidate.split()
        for word in words:
            word_lower = word.lower().rstrip('.')
            if word_lower in self.financial_terms:
                return False

        # Check for numbers
        if any(char.isdigit() for char in candidate):
            return False

        # Minimum length check
        if len(candidate.strip()) < 3:
            return False

        return True

    def _validate_with_spacy(self, candidates: List[str], context: str) -> List[Tuple[str, float]]:
        """
        Use spaCy to validate if candidates are real person names.

        Args:
            candidates: List of candidate name strings
            context: Full text context for validation

        Returns:
            List of (name, confidence) tuples for validated names
        """
        if not self.nlp:
            # Without spaCy, return all candidates with medium confidence
            return [(c, 0.7) for c in candidates]

        validated = []

        for candidate in candidates:
            # Create context snippet for better validation
            snippet = self._create_context_snippet(candidate, context)

            # Process with spaCy
            doc = self.nlp(snippet)

            # Check if candidate is recognized as PERSON
            is_person = False
            confidence = 0.0

            for ent in doc.ents:
                if ent.label_ == "PERSON" and candidate in ent.text:
                    is_person = True
                    confidence = 0.9
                    break

            # Also check title-cased version for all-caps names
            if not is_person and candidate.isupper():
                title_candidate = candidate.title()
                title_snippet = snippet.replace(candidate, title_candidate)
                title_doc = self.nlp(title_snippet)

                for ent in title_doc.ents:
                    if ent.label_ == "PERSON" and title_candidate in ent.text:
                        is_person = True
                        confidence = 0.85  # Slightly lower for all-caps
                        break

            if is_person:
                validated.append((candidate, confidence))

        return validated

    def _create_context_snippet(self, name: str, full_text: str, window: int = 50) -> str:
        """
        Create a context snippet around the name for better spaCy validation.

        Args:
            name: The name to find
            full_text: Full text
            window: Context window size in characters

        Returns:
            Context snippet containing the name
        """
        pos = full_text.find(name)
        if pos == -1:
            return name

        start = max(0, pos - window)
        end = min(len(full_text), pos + len(name) + window)

        return full_text[start:end]

    def _parse_name_components(self, validated_names: List[Tuple[str, float]]) -> List[Dict]:
        """
        Parse validated names into first/middle/last components.

        Args:
            validated_names: List of (name, confidence) tuples

        Returns:
            List of dicts with parsed components
        """
        parsed = []

        for name, confidence in validated_names:
            components = self._parse_single_name(name)
            parsed.append({
                'full_name': name,
                'first_name': components['first'],
                'middle_name': components['middle'],
                'last_name': components['last'],
                'confidence': confidence
            })

        return parsed

    def _parse_single_name(self, name: str) -> Dict[str, str]:
        """
        Parse a single name into components.

        Args:
            name: Full name string

        Returns:
            Dict with 'first', 'middle', 'last' keys
        """
        # Remove title if present
        title_pattern = r'^(?:Mr|Mrs|Ms|Dr|Prof|Rev)\.?\s+'
        name_without_title = re.sub(title_pattern, '', name, flags=re.IGNORECASE)

        # Split into words
        words = name_without_title.split()

        result = {
            'first': '',
            'middle': '',
            'last': ''
        }

        if len(words) == 1:
            # Single word name (unusual)
            result['last'] = words[0]
        elif len(words) == 2:
            # First Last
            result['first'] = words[0]
            result['last'] = words[1]
        elif len(words) == 3:
            # First Middle Last
            result['first'] = words[0]
            result['middle'] = words[1]
            result['last'] = words[2]
        elif len(words) > 3:
            # First Middle1 Middle2... Last
            result['first'] = words[0]
            result['middle'] = ' '.join(words[1:-1])
            result['last'] = words[-1]

        return result

    def _map_to_original_text(self, parsed_names: List[Dict], original_text: str) -> List[ParsedName]:
        """
        Map parsed names back to original PDF text positions.

        Args:
            parsed_names: List of parsed name dicts
            original_text: Original PDF text with newlines

        Returns:
            List of ParsedName objects with positions
        """
        final_names = []

        for name_info in parsed_names:
            full_name = name_info['full_name']
            positions = []

            # Find all occurrences in original text
            # Try exact match first
            start = 0
            while True:
                pos = original_text.find(full_name, start)
                if pos == -1:
                    break
                positions.append((pos, pos + len(full_name)))
                start = pos + 1

            # If no exact match, try with newlines normalized
            if not positions:
                # Try matching with various whitespace patterns
                pattern = re.escape(full_name)
                pattern = pattern.replace(r'\ ', r'\s+')  # Allow any whitespace

                for match in re.finditer(pattern, original_text):
                    positions.append((match.start(), match.end()))

            if positions:
                final_names.append(ParsedName(
                    full_name=full_name,
                    first_name=name_info['first_name'],
                    middle_name=name_info['middle_name'],
                    last_name=name_info['last_name'],
                    confidence=name_info['confidence'],
                    positions=positions
                ))

        return final_names


# Convenience function for integration
def detect_names_v2(page) -> List[ParsedName]:
    """
    Detect names in a PDF page using the v2 pipeline.

    Args:
        page: PyMuPDF page object

    Returns:
        List of ParsedName objects
    """
    detector = NameDetectorV2()
    return detector.detect_names_in_pdf(page)
