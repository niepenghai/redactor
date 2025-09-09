"""
Advanced address detection combining NLP and regex approaches.
"""
import re
import spacy
from typing import List, Tuple, Set, Optional
from dataclasses import dataclass

@dataclass
class AddressDetection:
    """Represents a detected address with confidence score."""
    text: str
    start: int
    end: int
    confidence: float
    detection_method: str

class HybridAddressDetector:
    """
    Combines spaCy NLP with refined regex patterns for optimal address detection.
    """
    
    def __init__(self):
        """Initialize the hybrid address detector."""
        self.nlp = None
        self._load_spacy_model()
        
    def _load_spacy_model(self):
        """Load spaCy model if available."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("🤖 Loaded spaCy model for enhanced address detection")
        except OSError:
            print("⚠️  spaCy model not found, using regex-only detection")
    
    def detect_addresses(self, text: str) -> List[AddressDetection]:
        """
        Detect addresses using hybrid approach.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected addresses with positions and confidence scores
        """
        addresses = []
        
        # Method 1: Enhanced regex patterns
        regex_addresses = self._detect_with_regex(text)
        addresses.extend(regex_addresses)
        
        # Method 2: NLP-enhanced detection (if available)
        if self.nlp:
            nlp_addresses = self._detect_with_nlp(text)
            addresses.extend(nlp_addresses)
        
        # Remove overlapping and clean up results
        return self._clean_and_deduplicate(addresses)
    
    def _detect_with_regex(self, text: str) -> List[AddressDetection]:
        """Enhanced regex-based address detection."""
        addresses = []
        
        # Pattern 1: Street addresses with improved handling
        street_patterns = [
            # Standard format: Number Street Type [, Suite/Apt Info]
            r'\b\d+\s+[A-Za-z][A-Za-z0-9\s]*\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Court|Ct|Place|Pl|Circle|Cir)(?:\s*,?\s*(?:Suite|Ste|Apt|Apartment|Unit|#)\s*[A-Za-z0-9-]+)?\b',
            
            # P.O. Box addresses
            r'\bP\.?\s*O\.?\s*Box\s+\d+\b',
            
            # Rural route addresses
            r'\b(?:Rural\s+Route|RR|HC)\s+\d+(?:\s+Box\s+\d+)?\b'
        ]
        
        for pattern in street_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                address_text = self._clean_address_text(match.group())
                if self._is_valid_address(address_text):
                    addresses.append(AddressDetection(
                        text=address_text,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.8,
                        detection_method="regex_street"
                    ))
        
        # Pattern 2: City, State ZIP (with comma)
        city_state_comma_pattern = r'\b[A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?\b'
        for match in re.finditer(city_state_comma_pattern, text):
            address_text = self._clean_address_text(match.group())
            addresses.append(AddressDetection(
                text=address_text,
                start=match.start(),
                end=match.end(),
                confidence=0.9,
                detection_method="regex_city_state_comma"
            ))
        
        # Pattern 3: City State ZIP (without comma) - be more restrictive to avoid false positives
        city_state_no_comma_pattern = r'\b[A-Z]{2,}(?:\s+[A-Z]{2,})*\s+[A-Z]{2}\s+\d{5}(?:-\d{4})?\b'
        for match in re.finditer(city_state_no_comma_pattern, text):
            candidate = self._clean_address_text(match.group())
            words = candidate.split()
            
            # Validate this looks like City State ZIP (last word is ZIP, second-to-last is 2-letter state)
            if len(words) >= 3 and len(words[-2]) == 2 and words[-2].isupper():
                addresses.append(AddressDetection(
                    text=candidate,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.85,
                    detection_method="regex_city_state_no_comma"
                ))
        
        return addresses
    
    def _detect_with_nlp(self, text: str) -> List[AddressDetection]:
        """NLP-enhanced address detection using spaCy."""
        addresses = []
        doc = self.nlp(text)
        
        # Look for address-like patterns in sentences
        for sent in doc.sents:
            sent_text = sent.text.strip()
            sent_start = sent.start_char
            
            # Find potential addresses within the sentence
            potential_addresses = self._extract_address_candidates(sent_text, sent_start)
            
            for addr_text, start_pos, end_pos in potential_addresses:
                # Use NLP to validate the address candidate
                confidence = self._assess_address_with_nlp(addr_text, sent_text)
                
                if confidence > 0.6:  # Threshold for acceptance
                    addresses.append(AddressDetection(
                        text=addr_text,
                        start=start_pos,
                        end=end_pos,
                        confidence=confidence,
                        detection_method="nlp_enhanced"
                    ))
        
        return addresses
    
    def _extract_address_candidates(self, sentence: str, sentence_start: int) -> List[Tuple[str, int, int]]:
        """Extract potential address candidates from a sentence."""
        candidates = []
        
        # Enhanced patterns that work better with NLP context
        patterns = [
            # Number + words + street type + optional suite info
            r'(\d+\s+[A-Za-z][A-Za-z0-9\s,]*?\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Court|Ct|Place|Pl)(?:\s*,?\s*(?:Suite|Ste|Apt|Apartment|Unit|#)\s*[A-Za-z0-9-]+)?)',
            
            # P.O. Box with various formats
            r'(P\.?\s*O\.?\s*Box\s+\d+)',
            
            # City, State ZIP
            r'([A-Z][a-zA-Z\s]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?)'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, sentence, re.IGNORECASE):
                candidate = self._clean_address_text(match.group(1))
                start_pos = sentence_start + match.start(1)
                end_pos = sentence_start + match.end(1)
                candidates.append((candidate, start_pos, end_pos))
        
        return candidates
    
    def _assess_address_with_nlp(self, address_candidate: str, context: str) -> float:
        """Use NLP to assess if a candidate is likely a real address."""
        if not self.nlp:
            return 0.7  # Default confidence without NLP
        
        doc = self.nlp(address_candidate)
        context_doc = self.nlp(context.lower())
        
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on NLP analysis
        has_number = any(token.like_num for token in doc)
        has_proper_noun = any(token.pos_ in ['PROPN', 'NOUN'] for token in doc)
        has_address_indicators = any(token.lemma_ in ['street', 'avenue', 'road', 'drive', 'lane', 'boulevard'] for token in doc)
        
        if has_number:
            confidence += 0.2
        if has_proper_noun:
            confidence += 0.1
        if has_address_indicators:
            confidence += 0.2
        
        # Check context for address-related terms
        address_context_terms = ['address', 'location', 'street', 'mail', 'send', 'visit', 'located', 'at']
        if any(term in context.lower() for term in address_context_terms):
            confidence += 0.1
        
        # Reduce confidence if it looks like business name only
        business_terms = ['bank', 'corp', 'company', 'inc', 'llc', 'services']
        if any(term in address_candidate.lower() for term in business_terms):
            confidence -= 0.2
        
        return min(confidence, 1.0)
    
    def _clean_address_text(self, address: str) -> str:
        """Clean up address text by removing extra whitespace and formatting."""
        # Remove excessive whitespace and newlines
        cleaned = re.sub(r'\s+', ' ', address.strip())
        
        # Remove leading/trailing punctuation except for periods in abbreviations
        cleaned = re.sub(r'^[,\-\s]+|[,\-\s]+$', '', cleaned)
        
        return cleaned
    
    def _is_valid_address(self, address: str) -> bool:
        """Basic validation for address candidates."""
        # Too short or too long addresses are likely false positives
        if len(address) < 5 or len(address) > 100:
            return False
        
        # Must contain at least one number and one letter
        has_number = any(char.isdigit() for char in address)
        has_letter = any(char.isalpha() for char in address)
        
        return has_number and has_letter
    
    def _clean_and_deduplicate(self, addresses: List[AddressDetection]) -> List[AddressDetection]:
        """Remove overlapping and duplicate addresses, keeping highest confidence ones."""
        if not addresses:
            return addresses
        
        # Sort by confidence (descending) then by position
        addresses.sort(key=lambda x: (-x.confidence, x.start))
        
        cleaned = []
        for addr in addresses:
            # Check if this address overlaps with or is very similar to existing ones
            is_duplicate = False
            
            for existing in cleaned:
                # Check for overlap in position
                if (addr.start < existing.end and addr.end > existing.start):
                    is_duplicate = True
                    break
                
                # Check for text similarity (same address detected by different methods)
                if self._addresses_are_similar(addr.text, existing.text):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                cleaned.append(addr)
        
        # Sort final results by position
        return sorted(cleaned, key=lambda x: x.start)
    
    def _addresses_are_similar(self, addr1: str, addr2: str) -> bool:
        """Check if two addresses are essentially the same."""
        # Normalize addresses for comparison
        norm1 = re.sub(r'\W+', ' ', addr1.lower()).strip()
        norm2 = re.sub(r'\W+', ' ', addr2.lower()).strip()
        
        # Check for substantial overlap
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        
        if not words1 or not words2:
            return False
        
        # If 80% of words overlap, consider them the same address
        overlap = len(words1.intersection(words2))
        min_words = min(len(words1), len(words2))
        
        return overlap / min_words > 0.8

# Convenience functions for integration
def detect_addresses_hybrid(text: str) -> List[Tuple[str, int, int]]:
    """
    Detect addresses using hybrid approach.
    
    Returns:
        List of (address_text, start_position, end_position) tuples
    """
    detector = HybridAddressDetector()
    detections = detector.detect_addresses(text)
    
    return [(detection.text, detection.start, detection.end) for detection in detections]