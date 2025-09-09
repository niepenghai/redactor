"""
NLP-based name detection for more accurate personal name identification.
"""
import re
from typing import List, Tuple, Set, Optional
from dataclasses import dataclass

@dataclass
class NameDetection:
    """Represents a detected name with its position and confidence."""
    text: str
    start: int
    end: int
    confidence: float
    entity_type: str

class SimpleNLPNameDetector:
    """
    Lightweight NLP-based name detector that doesn't require external dependencies.
    Uses linguistic patterns and context clues to identify personal names.
    """
    
    def __init__(self):
        """Initialize the name detector with built-in rules."""
        self.first_names = self._load_common_first_names()
        self.last_names = self._load_common_last_names()
        self.business_indicators = self._load_business_indicators()
        self.titles = {'Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'Rev', 'Miss'}
        
    def _load_common_first_names(self) -> Set[str]:
        """Load common first names for detection."""
        return {
            # Male names
            'James', 'Robert', 'John', 'Michael', 'William', 'David', 'Richard', 'Joseph',
            'Thomas', 'Christopher', 'Charles', 'Daniel', 'Matthew', 'Anthony', 'Mark',
            'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua', 'Kenneth', 'Kevin', 'Brian',
            'George', 'Timothy', 'Ronald', 'Edward', 'Jason', 'Jeffrey', 'Ryan', 'Jacob',
            
            # Female names  
            'Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan',
            'Jessica', 'Sarah', 'Karen', 'Lisa', 'Nancy', 'Betty', 'Helen', 'Sandra',
            'Donna', 'Carol', 'Ruth', 'Sharon', 'Michelle', 'Laura', 'Sarah', 'Kimberly',
            'Deborah', 'Dorothy', 'Lisa', 'Nancy', 'Karen', 'Betty', 'Helen', 'Sandra',
            
            # Additional common names
            'Alex', 'Chris', 'Jordan', 'Taylor', 'Casey', 'Riley', 'Morgan', 'Jamie',
            'Grace', 'Emma', 'Olivia', 'Sophia', 'Isabella', 'Mia', 'Charlotte', 'Amelia',
            
            # Common Asian names
            'Wei', 'Li', 'Ming', 'Xia', 'Lin', 'Chen', 'Wang', 'Zhang', 'Liu', 'Yang',
            'Qizhi', 'Jian', 'Lei', 'Mei', 'Jun', 'Ling', 'Hui', 'Ping', 'Qing', 'Fang'
        }
    
    def _load_common_last_names(self) -> Set[str]:
        """Load common last names for detection."""
        return {
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
            'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
            'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
            'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
            'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
            'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell',
            
            # Common Asian last names  
            'Chen', 'Wang', 'Li', 'Zhang', 'Liu', 'Yang', 'Huang', 'Zhao', 'Wu', 'Zhou',
            'Xu', 'Sun', 'Ma', 'Zhu', 'Hu', 'Guo', 'He', 'Lin', 'Gao', 'Luo', 'Zheng',
            'Liang', 'Xie', 'Tang', 'Song', 'Deng', 'Han', 'Cao', 'Feng', 'Peng', 'Zeng'
        }
    
    def _load_business_indicators(self) -> Set[str]:
        """Load terms that indicate business names rather than personal names."""
        return {
            'Bank', 'Corp', 'Corporation', 'Inc', 'Incorporated', 'LLC', 'Co', 'Company',
            'Group', 'Financial', 'Services', 'Credit', 'Union', 'Trust', 'Fund', 'Capital',
            'Investment', 'Holdings', 'Partners', 'Associates', 'Solutions', 'Technologies',
            'Systems', 'Networks', 'Communications', 'Insurance', 'Wells', 'Fargo', 'Chase',
            'Citibank', 'America', 'National', 'First', 'United', 'State', 'Federal',
            'Regional', 'Community', 'Central', 'Mutual', 'Savings', 'Loan'
        }
    
    def detect_names_in_text(self, text: str) -> List[NameDetection]:
        """
        Detect personal names in text using NLP-like analysis.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected names with positions and confidence scores
        """
        names = []
        
        # Find potential name patterns - enhanced for various formats
        patterns = [
            # Standard mixed case patterns
            r'\b[A-Z][a-z]{2,}\s+[A-Z]\.\s+[A-Z][a-z]{2,}\b',  # First M. Last
            r'\b[A-Z][a-z]{2,}\s+[A-Z]\s+[A-Z][a-z]{2,}\b',    # First M Last (no period)
            r'\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\b',            # First Last
            
            # All caps patterns (common in financial documents)
            r'\b[A-Z]{3,}\s+[A-Z]\.\s+[A-Z]{3,}\b',            # FIRST M. LAST
            r'\b[A-Z]{3,}\s+[A-Z]\s+[A-Z]{3,}\b',              # FIRST M LAST
            r'\b[A-Z]{3,}\s+[A-Z]{3,}\b',                      # FIRST LAST
            
            # Title patterns
            r'\b(?:Mr|Mrs|Ms|Dr|Prof|Rev)\.?\s+[A-Z][a-z]{2,}(?:\s+[A-Z]\.?\s*)?(?:\s+[A-Z][a-z]{2,})?\b',  # Title patterns
            
            # Last-name-first patterns (Chen, Grace L)
            r'\b[A-Z][a-z]{2,},\s+[A-Z][a-z]{2,}(?:\s+[A-Z]\.?)?\b',        # Last, First M.
            r'\b[A-Z]{3,},\s*[A-Z][a-z]{2,}(?:\s+[A-Z])?\b',               # LAST, First M
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                candidate = match.group().strip()
                start_pos = match.start()
                end_pos = match.end()
                
                # Analyze the candidate
                confidence, entity_type = self._analyze_name_candidate(candidate, text, start_pos)
                
                if confidence > 0.5:  # Threshold for name detection
                    names.append(NameDetection(
                        text=candidate,
                        start=start_pos,
                        end=end_pos,
                        confidence=confidence,
                        entity_type=entity_type
                    ))
        
        # Remove overlapping detections, keeping higher confidence ones
        return self._remove_overlapping_names(names)
    
    def _is_likely_business_context(self, candidate: str, context_before: str, context_after: str) -> bool:
        """Check if the candidate appears in a business context."""
        business_contexts = [
            'bank', 'corp', 'company', 'inc', 'llc', 'financial', 'services',
            'credit union', 'trust company', 'customer service', 'representative',
            'institution', 'organization', 'department'
        ]
        
        full_context = (context_before + " " + candidate + " " + context_after).lower()
        return any(term in full_context for term in business_contexts)
    
    def _analyze_name_candidate(self, candidate: str, full_text: str, position: int) -> Tuple[float, str]:
        """
        Analyze a candidate string to determine if it's likely a personal name.
        
        Returns:
            Tuple of (confidence_score, entity_type)
        """
        words = candidate.split()
        if len(words) > 4:  # Too many words, likely not a name
            return 0.0, "UNKNOWN"
        
        # Check for business indicators
        if any(word in self.business_indicators for word in words):
            return 0.0, "BUSINESS"
        
        # Check context around the name
        context_before = full_text[max(0, position-50):position].lower()
        context_after = full_text[position+len(candidate):position+len(candidate)+50].lower()
        
        # Check if in business context, but override for clear personal name indicators
        personal_name_indicators = [
            'account holder:', 'customer name:', 'dear ', 'signature:', 'name:', 
            'holder:', 'client:', 'mr.', 'mrs.', 'ms.', 'dr.'
        ]
        
        has_personal_indicator = any(
            indicator in context_before.lower() + context_after.lower() 
            for indicator in personal_name_indicators
        )
        
        if self._is_likely_business_context(candidate, context_before, context_after) and not has_personal_indicator:
            return 0.1, "BUSINESS_CONTEXT"
        
        confidence = 0.0
        entity_type = "PERSON"
        
        # Title-based detection (highest confidence)
        if any(word.rstrip('.') in self.titles for word in words):
            confidence = 0.95
            entity_type = "PERSON_WITH_TITLE"
        
        # Context-based detection - but make sure it's actually a name-like candidate
        elif any(indicator in context_before for indicator in [
            'account holder', 'customer name', 'signed by', 'signature', 'name:', 'dear'
        ]):
            # Additional check: make sure the candidate doesn't contain business terms
            if not any(business_word in candidate.lower() for business_word in ['number', 'balance', 'summary', 'statement', 'service']):
                confidence = 0.9
                entity_type = "PERSON_CONTEXTUAL"
            else:
                confidence = 0.0  # Reject if it contains business terms
        
        # Name pattern analysis
        elif len(words) == 2:  # First Last pattern
            first, last = words[0], words[1]
            
            # Check against known names (case-insensitive)
            first_score = 1.0 if first.title() in self.first_names else 0.0
            last_score = 1.0 if last.title() in self.last_names else 0.0
            
            # Check for business/financial terms in either position
            business_first_words = {'Account', 'Customer', 'Service', 'Banking', 'Online', 'Mobile', 'Direct', 'Total', 'Current', 'Available', 'Wells', 'Main', 'First', 'Second', 'Third'}
            business_last_words = {'Number', 'Balance', 'Summary', 'Statement', 'Service', 'Banking', 'Deposit', 'Withdrawal', 'Transfer', 'Street', 'Avenue', 'Road', 'Drive', 'Fargo'}
            
            if first in business_first_words or last in business_last_words:
                return 0.0, "BUSINESS_TERM"
            
            # Linguistic patterns
            if first_score == 0.0:
                # Check if it looks like a first name (common endings, length)
                if len(first) >= 3 and any(first.endswith(ending) for ending in ['son', 'er', 'ly', 'an', 'en']):
                    first_score = 0.3
                elif len(first) >= 4:
                    first_score = 0.2
            
            if last_score == 0.0:
                # Check if it looks like a last name
                if any(last.endswith(ending) for ending in ['son', 'sen', 'ez', 'ski', 'owski']):
                    last_score = 0.4
                elif len(last) >= 3:
                    last_score = 0.2
            
            confidence = (first_score + last_score) / 2
            
            # Boost confidence if capitalization pattern is right
            if first[0].isupper() and first[1:].islower() and last[0].isupper() and last[1:].islower():
                confidence += 0.1
                
        elif len(words) == 3:  # First Middle Last or Title First Last
            if words[0].rstrip('.') in self.titles:
                confidence = 0.9
                entity_type = "PERSON_WITH_TITLE"
            elif len(words[1]) == 2 and words[1].endswith('.'):  # Middle initial with period (M.)
                confidence = 0.8
                entity_type = "PERSON_WITH_MIDDLE"
            elif len(words[1]) == 1 and words[1].isupper():  # Single letter middle initial (L)
                confidence = 0.75
                entity_type = "PERSON_WITH_MIDDLE_INITIAL"
        
        # Reduce confidence if it appears in business context BUT NOT when we have personal indicators
        if any(term in context_before + context_after for term in ['bank', 'corp', 'company', 'inc']) and not has_personal_indicator:
            confidence *= 0.3
        
        return min(confidence, 1.0), entity_type
    
    def _remove_overlapping_names(self, names: List[NameDetection]) -> List[NameDetection]:
        """Remove overlapping name detections, keeping higher confidence ones."""
        if not names:
            return names
        
        # Sort by confidence (descending) then by position
        names.sort(key=lambda x: (-x.confidence, x.start))
        
        result = []
        for name in names:
            # Check if this name overlaps with any already selected name
            overlaps = False
            for existing in result:
                if (name.start < existing.end and name.end > existing.start):
                    overlaps = True
                    break
            
            if not overlaps:
                result.append(name)
        
        return sorted(result, key=lambda x: x.start)  # Sort by position for final result

# Fallback for when NLP libraries aren't available
def detect_names_simple(text: str) -> List[Tuple[str, int, int]]:
    """
    Simple fallback name detection without external dependencies.
    
    Returns:
        List of (name_text, start_position, end_position) tuples
    """
    detector = SimpleNLPNameDetector()
    detections = detector.detect_names_in_text(text)
    
    return [(detection.text, detection.start, detection.end) for detection in detections]

# Try to import spaCy for more advanced NLP, fall back to simple detector
try:
    import spacy
    
    class SpacyNameDetector:
        """Advanced name detector using spaCy NLP."""
        
        def __init__(self):
            """Initialize spaCy model."""
            self.nlp = None
            self.simple_detector = SimpleNLPNameDetector()
            
            try:
                # Try to load small English model first
                self.nlp = spacy.load("en_core_web_sm")
                print("🤖 Loaded spaCy en_core_web_sm model for advanced NER")
            except OSError:
                try:
                    # Try medium model
                    self.nlp = spacy.load("en_core_web_md")
                    print("🤖 Loaded spaCy en_core_web_md model for advanced NER")
                except OSError:
                    print("⚠️  No spaCy models found, using simple detector")
        
        def _looks_like_person_name(self, name: str) -> bool:
            """Check if a text looks like a person name."""
            if not name or len(name.strip()) < 2:
                return False
                
            # Should have alphabetic characters and spaces
            if not re.match(r'^[A-Za-z\s\-\'\.]+$', name):
                return False
                
            # Should not be all numbers or have too many numbers
            if any(char.isdigit() for char in name):
                return False
                
            # Split into words and check basic name patterns
            words = name.strip().split()
            if len(words) < 1 or len(words) > 4:  # Names typically 1-4 words
                return False
                
            # Each word should look like a name part
            for word in words:
                if len(word) < 1:
                    continue
                # Should not be obvious non-name words
                if word.lower() in ['st', 'street', 'ave', 'avenue', 'rd', 'road', 'dr', 'drive', 'ca', 'tx', 'ny', 'fl']:
                    return False
                    
            return True

        def _looks_like_address(self, text: str) -> bool:
            """Check if text looks like an address rather than a person name."""
            text_lower = text.lower()
            
            # Common address patterns that spaCy might misidentify as names
            address_indicators = [
                # State codes
                ' ca ', ' tx ', ' ny ', ' fl ', ' il ', ' pa ', ' oh ', ' mi ', ' ga ', ' nc ',
                ' va ', ' wa ', ' az ', ' ma ', ' in ', ' tn ', ' mo ', ' md ', ' wi ', ' mn ',
                ' co ', ' al ', ' sc ', ' la ', ' ky ', ' or ', ' ok ', ' ct ', ' ut ', ' nv ',
                ' ar ', ' ms ', ' ks ', ' nm ', ' ne ', ' wv ', ' id ', ' hi ', ' nh ', ' me ',
                ' mt ', ' ri ', ' de ', ' sd ', ' nd ', ' ak ', ' vt ', ' wy ',
                
                # ZIP codes
                r'\d{5}(-\d{4})?',
                
                # Common address words
                'street', 'st ', 'avenue', 'ave ', 'road', 'rd ', 'drive', 'dr ',
                'boulevard', 'blvd', 'lane', 'ln ', 'court', 'ct ', 'circle', 'cir',
                'place', 'pl ', 'way', 'terrace', 'ter', 'square', 'sq',
                
                # P.O. Box patterns
                'p.o. box', 'po box', 'post office box'
            ]
            
            # Check for address indicators
            import re
            for indicator in address_indicators:
                if indicator.startswith('\\') and indicator.endswith(')?'):
                    # Regex pattern
                    if re.search(indicator, text_lower):
                        return True
                else:
                    # Simple string match
                    if indicator in text_lower:
                        return True
            
            return False

        def _is_business_name(self, name: str, context: str) -> bool:
            """Enhanced business name detection using both rules and context."""
            name_lower = name.lower()
            context_lower = context.lower()
            
            # Check if this looks like an address (common cause of false positives)
            if self._looks_like_address(name):
                return True
            
            # Direct business name indicators
            business_terms = [
                'bank', 'corp', 'corporation', 'inc', 'incorporated', 'llc', 'ltd',
                'company', 'co', 'group', 'financial', 'services', 'credit', 'union',
                'trust', 'fund', 'capital', 'investment', 'holdings', 'partners',
                'associates', 'solutions', 'technologies', 'systems', 'networks',
                'insurance', 'mutual', 'savings', 'loan', 'authority', 'agency',
                # Banking/transaction terms that spaCy often confuses as names
                'deposit', 'withdrawal', 'transfer', 'payment', 'transaction',
                'overdraft', 'protection', 'interest', 'earned', 'fee', 'charge',
                'balance', 'available', 'current', 'pending', 'mobile', 'online',
                'direct', 'automatic', 'recurring', 'scheduled', 'wire', 'ach'
            ]
            
            # Known service/app names that are often misclassified as person names
            service_names = [
                'doordash', 'dashpass', 'uber', 'lyft', 'airbnb', 'netflix', 'spotify',
                'amazon', 'paypal', 'venmo', 'zelle', 'cashapp', 'apple', 'google',
                'microsoft', 'facebook', 'instagram', 'twitter', 'linkedin',
                'starbucks', 'mcdonalds', 'walmart', 'target', 'costco', 'best buy',
                'home depot', 'lowes', 'whole foods', 'kroger', 'safeway'
            ]
            
            # Check if name contains business terms
            if any(term in name_lower for term in business_terms):
                return True
            
            # Check if name contains known service/app names
            if any(service in name_lower for service in service_names):
                return True
            
            # Additional specific exclusions for common false positives
            words = name.split()
            if len(words) == 2:
                first_word, second_word = words[0].lower(), words[1].lower()
                # Common business/location patterns
                excluded_combinations = [
                    ('account', 'number'), ('account', 'balance'), ('account', 'summary'),
                    ('customer', 'service'), ('customer', 'number'), ('main', 'street'),
                    ('first', 'street'), ('second', 'avenue'), ('third', 'street'),
                    ('oak', 'avenue'), ('pine', 'road'), ('elm', 'drive'),
                    ('current', 'balance'), ('available', 'balance'), ('total', 'balance'),
                    ('online', 'banking'), ('mobile', 'banking'), ('direct', 'deposit'),
                    ('wire', 'transfer'), ('service', 'fee'), ('monthly', 'fee')
                ]
                if (first_word, second_word) in excluded_combinations:
                    return True
            
            # Known bank/financial institution names
            financial_institutions = [
                'wells fargo', 'bank of america', 'chase', 'citibank', 'goldman sachs',
                'morgan stanley', 'jpmorgan', 'american express', 'discover',
                'capital one', 'ally', 'schwab', 'fidelity', 'vanguard',
                'first national', 'united', 'state', 'federal', 'regional',
                'community', 'central', 'national'
            ]
            
            if any(inst in name_lower for inst in financial_institutions):
                return True
            
            # Context-based business detection
            business_contexts = [
                'customer service', 'representative', 'agent', 'department',
                'division', 'branch', 'office', 'institution', 'organization',
                'headquarters', 'corporation', 'enterprise', 'firm'
            ]
            
            if any(ctx in context_lower for ctx in business_contexts):
                return True
                
            return False
        
        def _smart_title_case(self, text: str) -> str:
            """Convert text to title case while preserving important formatting."""
            # Simple title case conversion for better NER on all-caps text
            # Only convert if the text appears to be mostly all caps
            words = text.split()
            caps_words = sum(1 for word in words if len(word) > 1 and word.isupper())
            
            if caps_words > len(words) * 0.3:  # If >30% words are all caps
                return text.title()
            return text
        
        def _could_be_person_name(self, text: str) -> bool:
            """Check if an ORG entity could actually be a person name."""
            # Clean the text
            clean_text = text.strip()
            words = clean_text.split()
            
            # Skip if too many words (likely a real organization)
            if len(words) > 4:
                return False
            
            # Skip if contains clear business indicators
            business_words = ['corp', 'inc', 'llc', 'ltd', 'company', 'bank', 'group', 'services']
            if any(word.lower() in business_words for word in words):
                return False
            
            # Check if it looks like a person name pattern
            if len(words) == 2:  # First Last
                return True
            elif len(words) == 3:  # First M Last or First Middle Last
                # Check for middle initial pattern
                if len(words[1]) <= 2:  # Middle initial
                    return True
            
            return False
        
        def detect_names_in_text(self, text: str) -> List[NameDetection]:
            """Detect names using spaCy NER with enhanced filtering."""
            if self.nlp is None:
                # Fall back to simple detector
                return self.simple_detector.detect_names_in_text(text)
            
            # Process both original text and title-cased version for better all-caps detection
            original_doc = self.nlp(text)
            
            # Create title-cased version for better NER on all-caps text
            title_cased_text = self._smart_title_case(text)
            title_doc = self.nlp(title_cased_text) if title_cased_text != text else None
            
            names = []
            processed_positions = set()  # Track processed positions to avoid duplicates
            
            # Process original document
            for ent in original_doc.ents:
                if ent.label_ == "PERSON":
                    # Get surrounding context for better filtering
                    start_context = max(0, ent.start_char - 100)
                    end_context = min(len(text), ent.end_char + 100)
                    context = text[start_context:end_context]
                    
                    # Filter out business names using enhanced detection
                    if not self._is_business_name(ent.text, context):
                        # Additional confidence scoring based on context
                        confidence = 0.95  # Base spaCy confidence
                        
                        # Boost confidence for names with clear personal indicators
                        personal_indicators = ['mr.', 'mrs.', 'ms.', 'dr.', 'account holder', 'signature']
                        if any(indicator in context.lower() for indicator in personal_indicators):
                            confidence = 0.98
                        
                        # Clean up the detected name text and split multi-line detections
                        clean_name = ent.text.strip()
                        
                        # Handle multi-line names by splitting on newlines and extracting valid names
                        if '\n' in clean_name:
                            lines = [line.strip() for line in clean_name.split('\n') if line.strip()]
                            current_pos = ent.start_char
                            
                            for line in lines:
                                # Check if this line looks like a person name
                                if self._looks_like_person_name(line):
                                    # Find the position of this line in the original text
                                    line_start = text.find(line, current_pos)
                                    if line_start != -1:
                                        position_key = (line_start, line_start + len(line))
                                        if position_key not in processed_positions:
                                            names.append(NameDetection(
                                                text=line,
                                                start=line_start,
                                                end=line_start + len(line),
                                                confidence=confidence,
                                                entity_type="PERSON_SPACY_SPLIT"
                                            ))
                                            processed_positions.add(position_key)
                                        current_pos = line_start + len(line)
                        else:
                            # Single line name
                            position_key = (ent.start_char, ent.end_char)
                            
                            if position_key not in processed_positions:
                                names.append(NameDetection(
                                    text=clean_name,
                                    start=ent.start_char,
                                    end=ent.start_char + len(clean_name),
                                    confidence=confidence,
                                    entity_type="PERSON_SPACY"
                                ))
                                processed_positions.add(position_key)
            
            # Process title-cased document if different from original (for all-caps names like XIA LIN)
            if title_doc:
                for ent in title_doc.ents:
                    if ent.label_ == "PERSON":
                        # Map back to original text position
                        original_text = text[ent.start_char:ent.end_char]
                        
                        # Get surrounding context from original text
                        start_context = max(0, ent.start_char - 100)
                        end_context = min(len(text), ent.end_char + 100)
                        context = text[start_context:end_context]
                        
                        if not self._is_business_name(original_text, context):
                            confidence = 0.92  # Slightly lower confidence for title-cased detection
                            
                            # Boost confidence for clear personal indicators
                            personal_indicators = ['mr.', 'mrs.', 'ms.', 'dr.', 'account holder', 'signature']
                            if any(indicator in context.lower() for indicator in personal_indicators):
                                confidence = 0.96
                                
                            # Handle multi-line names from title-cased processing too
                            if '\n' in original_text:
                                lines = [line.strip() for line in original_text.split('\n') if line.strip()]
                                current_pos = ent.start_char
                                
                                for line in lines:
                                    if self._looks_like_person_name(line):
                                        # Find the position of this line in the original text
                                        line_start = text.find(line, current_pos)
                                        if line_start != -1:
                                            position_key = (line_start, line_start + len(line))
                                            if position_key not in processed_positions:
                                                names.append(NameDetection(
                                                    text=line,
                                                    start=line_start,
                                                    end=line_start + len(line),
                                                    confidence=confidence,
                                                    entity_type="PERSON_SPACY_TITLECASE_SPLIT"
                                                ))
                                                processed_positions.add(position_key)
                                            current_pos = line_start + len(line)
                            else:
                                # Single line name
                                position_key = (ent.start_char, ent.end_char)
                                
                                if position_key not in processed_positions:
                                    names.append(NameDetection(
                                        text=original_text,
                                        start=ent.start_char,
                                        end=ent.start_char + len(original_text),
                                        confidence=confidence,
                                        entity_type="PERSON_SPACY_TITLECASE"
                                    ))
                                    processed_positions.add(position_key)
            
            # Also use the simple detector for names that spaCy might miss (especially all-caps international names)
            simple_detections = self.simple_detector.detect_names_in_text(text)
            for simple_detection in simple_detections:
                # Check if this overlaps with existing detections
                overlaps = any(
                    not (simple_detection.end <= existing.start or simple_detection.start >= existing.end)
                    for existing in names
                )
                
                if not overlaps and simple_detection.confidence > 0.7:
                    # Only add if it has high confidence from simple detector
                    names.append(simple_detection)
            
            return names
    
    # Use spaCy detector if available
    def detect_names_nlp(text: str) -> List[Tuple[str, int, int]]:
        """Detect names using advanced NLP."""
        try:
            detector = SpacyNameDetector()
            detections = detector.detect_names_in_text(text)
            return [(detection.text, detection.start, detection.end) for detection in detections]
        except:
            # Fall back to simple detector
            return detect_names_simple(text)

except ImportError:
    # spaCy not available, define dummy function
    def detect_names_nlp(text: str) -> List[Tuple[str, int, int]]:
        """Fallback to simple name detection."""
        return detect_names_simple(text)