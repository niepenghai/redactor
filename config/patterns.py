"""
Pattern definitions for financial document redaction.
"""
import re
from typing import List, Tuple, Dict, Any

# Import realistic generator and NLP name detector if available
try:
    from ..utils.realistic_generators import RealisticDataGenerator
    from ..utils.nlp_name_detector import detect_names_nlp
except ImportError:
    try:
        from utils.realistic_generators import RealisticDataGenerator
        from utils.nlp_name_detector import detect_names_nlp
    except ImportError:
        RealisticDataGenerator = None
        detect_names_nlp = None


# Business exclusions now handled by NLP-based name detection

def get_financial_patterns() -> Dict[str, List[Tuple[str, str]]]:
    """Define all financial redaction patterns with generic replacements."""
    return {
        # Social Security Numbers
        'ssn': [(r'\b(?:\d{3}-\d{2}-\d{4}|\d{9})\b', 'XXX-XX-XXXX')],
        
        # Phone numbers - more specific patterns
        'phone': [
            (r'\(\d{3}\)\s*\d{3}[-.\s]\d{4}', '(XXX) XXX-XXXX'),  # (555) 123-4567
            (r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b', 'XXX-XXX-XXXX'),     # 555-123-4567
            (r'\b1[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '1-XXX-XXX-XXXX'),  # 1-555-123-4567
        ],
        
        # Bank account numbers - more restrictive
        'account_number': [
            (r'(?i)(?:account|acct)\s*#?\s*:?\s*\d{8,17}\b', 'ACCOUNT XXXXXXXXXX'),  # With context
            (r'(?i)(?:account\s+number|account\s+#)\s+\d{8,17}\b', 'ACCOUNT XXXXXXXXXX'),  # Table format
            (r'(?i)(?:HIGH YIELD SAVINGS|SAVINGS|CHECKING)\s+\d{10,17}\b', 'ACCOUNT XXXXXXXXXX'),  # Account type + number
            (r'\b\d{4}\s+\d{4}\s+\d{4}\b', 'XXXX XXXX XXXX'),  # Spaced format: 0008 6117 4372
            (r'(?i)(?:banking|savings|checking).*?\b\d{4}\s+\d{4}\s+\d{4}\b', 'ACCOUNT XXXX XXXX XXXX'),  # Account type context with spaced number
            (r'\b\d{10,11}\b(?=.*(?:\$|balance|savings|statement))', 'XXXXXXXXXX'),  # 10-11 digits with financial context
            (r'\b\d{12,17}\b', 'XXXXXXXXXX'),  # 12+ digits only (more conservative)
        ],
        
        # Routing numbers (9 digits)
        'routing_number': [(r'\b\d{9}\b(?=.*routing|routing.*)', 'XXXXXXXXX')],
        
        # Credit card numbers (various formats)
        'credit_card': [
            (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', 'XXXX-XXXX-XXXX-XXXX'),  # 16 digits
            (r'\b(?:\d{4}[-\s]?)\d{6}[-\s]?\d{5}\b', 'XXXX-XXXXXX-XXXXX'),  # Amex 15 digits
        ],
        
        # Tax ID / EIN (XX-XXXXXXX)
        'tax_id': [(r'\b\d{2}-\d{7}\b', 'XX-XXXXXXX')],
        
        # Currency amounts (various formats) - excluding balance-related amounts
        # Balance amounts will be filtered out during processing
        'currency': [
            (r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?', '$X,XXX.XX'),
            (r'\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?(?=\s*(?:USD|dollars?))', 'X,XXX.XX'),
        ],
        
        # Dates (MM/DD/YYYY, MM-DD-YYYY, Month DD, YYYY)
        'dates': [
            (r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', 'XX/XX/XXXX'),
            (r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}\b', 'Month XX, XXXX'),
        ],
        
        # Email addresses
        'email': [(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'user@domain.com')],
        
        # Addresses - comprehensive address patterns
        'address': [
            # Street addresses with house numbers - very specific
            (r'\b\d{1,5}\s+[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+(STREET|ST|AVENUE|AVE|ROAD|RD|DRIVE|DR|LANE|LN|BOULEVARD|BLVD|WAY|PLACE|PL|CIRCLE|CIR|COURT|CT)(?:\s|$)', '[STREET ADDRESS]'),
            # City, State ZIP format
            (r'\b[A-Z][A-Za-z\s]+,?\s+[A-Z]{2}\s+\d{5}(?:-\d{4})?\b', '[CITY, STATE ZIP]'),
            # PO Box addresses
            (r'(?i)P\.?O\.?\s*BOX\s+\d+', 'P.O. BOX [NUMBER]'),
        ],
        
        # Employer information patterns
        'employer': [
            (r'(?i)employer:?\s*([^\n\r]+)', 'Employer: [EMPLOYER NAME]'),
            (r'(?i)company:?\s*([^\n\r]+)', 'Company: [COMPANY NAME]'),
        ],
        
        # Personal names - Now handled by NLP-based detection
        # Keep minimal fallback patterns for when NLP detection is unavailable
        'names': [
            # Names with clear titles (high confidence)
            (r'\b(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?)\s+[A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+\b', '[FULL NAME]'),
            # Names in very specific contexts (high confidence)
            (r'(?i)(?:account\s+holder|customer\s+name|patient\s+name|client\s+name):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)', 'Name: [FULL NAME]'),
            # Signature lines (high confidence)
            (r'(?i)signature:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)', 'Signature: [FULL NAME]'),
            # Special marker for NLP-based detection (processed separately)
            ('__NLP_NAMES__', '[FULL NAME]'),
        ]
    }


def get_pattern_generators() -> Dict[str, str]:
    """Map pattern categories to their generator methods."""
    return {
        'ssn': 'generate_ssn',
        'phone': 'generate_phone',
        'account_number': 'generate_account_number',
        'routing_number': 'generate_routing_number',
        'credit_card': 'generate_credit_card',
        'tax_id': 'generate_tax_id',
        'currency': 'generate_currency',
        'dates': 'generate_date',
        'email': 'generate_email',
        'address': 'generate_address',
        'employer': 'generate_employer_name',
        'names': 'generate_person_name'
    }


def get_enhanced_patterns(config: Dict[str, Any]) -> Dict[str, List[Tuple[str, str]]]:
    """Get patterns with replacements based on configuration mode."""
    base_patterns = get_financial_patterns()
    replacement_mode = config.get("replacement_mode", "generic")
    
    if replacement_mode == "generic":
        return base_patterns
    elif replacement_mode == "realistic" and RealisticDataGenerator:
        return _generate_realistic_patterns(config, base_patterns)
    elif replacement_mode == "custom":
        return _generate_custom_patterns(config, base_patterns)
    else:
        # Fallback to generic if realistic generator not available
        return base_patterns


def _generate_realistic_patterns(config: Dict[str, Any], base_patterns: Dict[str, List[Tuple[str, str]]]) -> Dict[str, List[Tuple[str, str]]]:
    """Generate patterns with realistic replacements."""
    if not RealisticDataGenerator:
        return base_patterns
    
    generator = RealisticDataGenerator(config)
    enhanced_patterns = {}
    pattern_generators = get_pattern_generators()
    
    for category, patterns in base_patterns.items():
        enhanced_patterns[category] = []
        
        for pattern, default_replacement in patterns:
            if category in pattern_generators:
                # Use realistic replacement - we'll generate this dynamically during redaction
                enhanced_patterns[category].append((pattern, f"REALISTIC_{category.upper()}"))
            else:
                # Keep original replacement for categories without generators
                enhanced_patterns[category].append((pattern, default_replacement))
    
    return enhanced_patterns


def _generate_custom_patterns(config: Dict[str, Any], base_patterns: Dict[str, List[Tuple[str, str]]]) -> Dict[str, List[Tuple[str, str]]]:
    """Generate patterns with custom replacements from config."""
    enhanced_patterns = base_patterns.copy()
    
    # Get custom replacement mappings from config
    custom_replacements = config.get("replacement_settings", {}).get("custom_replacements", {})
    
    for category, patterns in enhanced_patterns.items():
        if category in custom_replacements:
            custom_replacement = custom_replacements[category]
            # Update all patterns in this category
            enhanced_patterns[category] = [(pattern, custom_replacement) for pattern, _ in patterns]
    
    return enhanced_patterns


def get_patterns_for_document_type(doc_type: str, financial_patterns: Dict[str, List[Tuple[str, str]]]) -> List[Tuple[str, str]]:
    """Get specific redaction patterns based on document type."""
    base_patterns = financial_patterns['ssn'] + financial_patterns['phone'] + financial_patterns['email'] + financial_patterns['names']
    
    if doc_type == 'bank_statement':
        return (base_patterns + 
                financial_patterns['account_number'] + 
                financial_patterns['routing_number'] + 
                financial_patterns['currency'] + 
                financial_patterns['address'])
    
    elif doc_type == 'w2':
        return (base_patterns + 
                financial_patterns['tax_id'] + 
                financial_patterns['currency'] + 
                financial_patterns['employer'] + 
                financial_patterns['address'])
    
    elif doc_type == 'tax_return':
        return (base_patterns + 
                financial_patterns['tax_id'] + 
                financial_patterns['currency'] + 
                financial_patterns['address'])
    
    elif doc_type == 'pay_stub':
        return (base_patterns + 
                financial_patterns['currency'] + 
                financial_patterns['employer'] + 
                financial_patterns['address'])
    
    else:  # general
        patterns = []
        for category_patterns in financial_patterns.values():
            patterns.extend(category_patterns)
        return patterns


def filter_patterns_by_config(patterns: List[Tuple[str, str]], enabled_patterns: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Filter document patterns based on configuration settings."""
    filtered_patterns = []
    for pattern, replacement in patterns:
        # Check if this pattern is in our enabled patterns
        if any(p[0] == pattern for p in enabled_patterns):
            filtered_patterns.append((pattern, replacement))
    return filtered_patterns


def get_nlp_name_patterns(text: str) -> List[Tuple[str, str]]:
    """
    Get name patterns using NLP detection instead of regex.
    
    Args:
        text: The text to analyze for names
        
    Returns:
        List of (detected_name, replacement) tuples
    """
    if detect_names_nlp is None:
        # NLP detector not available, return empty list
        print("⚠️  NLP name detection not available, using fallback regex patterns only")
        return []
    
    try:
        # Use NLP to detect names in the text
        detected_names = detect_names_nlp(text)
        
        # Convert to pattern format
        name_patterns = []
        for name, start, end in detected_names:
            # Create exact match pattern for this specific name
            escaped_name = re.escape(name)

            # 1. Exact pattern with word boundaries
            exact_pattern = f"\\b{escaped_name}\\b"
            name_patterns.append((exact_pattern, '[FULL NAME]'))

            # 2. Extended pattern to catch variations like "STEPHENIE SYCHR P2P"
            # Match the name followed by optional whitespace and alphanumeric/common suffixes
            if ' ' in name:  # Only for multi-word names
                extended_pattern = f"\\b{escaped_name}(?:\\s+[A-Z0-9P]+)*\\b"
                name_patterns.append((extended_pattern, '[FULL NAME]'))

        return name_patterns
        
    except Exception as e:
        print(f"⚠️  Error in NLP name detection: {e}")
        return []


def enhance_patterns_with_nlp(base_patterns: Dict[str, List[Tuple[str, str]]], text: str) -> Dict[str, List[Tuple[str, str]]]:
    """
    Enhance patterns with NLP-detected names for the specific text.
    
    Args:
        base_patterns: Base pattern dictionary
        text: Text to analyze for name detection
        
    Returns:
        Enhanced patterns with NLP-detected names
    """
    enhanced_patterns = base_patterns.copy()
    
    # Get NLP-detected name patterns for this specific text
    nlp_name_patterns = get_nlp_name_patterns(text)
    
    if nlp_name_patterns:
        # Replace the __NLP_NAMES__ marker with actual detected patterns
        names_patterns = []
        for pattern, replacement in enhanced_patterns['names']:
            if pattern == '__NLP_NAMES__':
                # Add all NLP-detected name patterns
                names_patterns.extend(nlp_name_patterns)
            else:
                # Keep other patterns
                names_patterns.append((pattern, replacement))
        
        enhanced_patterns['names'] = names_patterns
        print(f"🤖 NLP detected {len(nlp_name_patterns)} name patterns")
    else:
        # Remove the __NLP_NAMES__ marker if no NLP patterns found
        enhanced_patterns['names'] = [
            (pattern, replacement) 
            for pattern, replacement in enhanced_patterns['names'] 
            if pattern != '__NLP_NAMES__'
        ]
    
    return enhanced_patterns


def get_pattern_priority() -> Dict[str, int]:
    """
    Define priority order for patterns when multiple patterns match the same text.
    Lower number = higher priority (will be applied first).
    """
    return {
        'ssn': 1,              # Highest priority - very specific
        'credit_card': 2,      # High priority - specific format
        'phone': 3,            # High priority - formatted
        'email': 4,            # High priority - specific format
        'names': 5,            # Medium-high priority - NLP detection
        'tax_id': 6,           # Medium priority
        'routing_number': 7,   # Medium priority
        'account_number': 8,   # Lower priority - can be generic
        'address': 9,          # Lower priority - can be broad
        'dates': 10,           # Low priority - very common
        'currency': 11,        # Low priority - common
        'employer': 12,        # Lowest priority - context dependent
    }


# Pre-compiled balance keywords for performance
_BALANCE_KEYWORDS = [
    'beginning balance:', 'ending balance:', 'available balance:',
    'current balance:', 'account balance:', 'total balance:',
    'statement balance:', 'opening balance:', 'closing balance:',
    'beginning balance ', 'ending balance ', 'available balance ',
    'current balance ', 'account balance ', 'total balance ',
    'statement balance ', 'opening balance ', 'closing balance ',
    # Add keywords without colon/space for multi-line formats
    'beginning balance', 'ending balance', 'available balance',
    'current balance', 'account balance', 'total balance',
    'statement balance', 'opening balance', 'closing balance'
]

def is_balance_amount(text: str, start_pos: int, full_text: str) -> bool:
    """
    Check if a currency match is a balance amount that should be preserved.
    Optimized version with reduced string operations.

    Args:
        text: The matched currency text
        start_pos: Starting position of the match in full_text
        full_text: The complete text being processed

    Returns:
        True if this is a balance amount that should not be redacted
    """
    # Quick optimization: get smaller context first (50 chars instead of 200)
    context_start = max(0, start_pos - 50)
    before_context = full_text[context_start:start_pos].lower()

    # Quick check with short context first
    for keyword in _BALANCE_KEYWORDS:
        if keyword in before_context:
            return True

    # Only do expensive line-based check if quick check failed
    # Get current line context
    line_start = full_text.rfind('\n', 0, start_pos) + 1
    line_end = full_text.find('\n', start_pos + len(text))
    if line_end == -1:
        line_end = len(full_text)

    # Only check line if it's different from what we already checked
    if line_start < context_start:
        line_context = full_text[line_start:start_pos].lower()
        amount_pos_in_line = start_pos - line_start

        for keyword in _BALANCE_KEYWORDS:
            keyword_pos = line_context.find(keyword)
            if keyword_pos != -1 and keyword_pos < amount_pos_in_line:
                return True

    return False


def filter_balance_amounts(matches: List[Tuple[str, str, int, int, str]], full_text: str) -> List[Tuple[str, str, int, int, str]]:
    """
    Filter out balance amounts from currency matches.
    Optimized version with early exit and reduced operations.

    Args:
        matches: List of (text, replacement, start, end, category) tuples
        full_text: The complete text being processed

    Returns:
        Filtered list with balance amounts removed
    """
    # Early exit if no matches
    if not matches:
        return matches

    # Quick check: if there are no currency matches, return as-is
    has_currency = any(category == 'currency' for _, _, _, _, category in matches)
    if not has_currency:
        return matches

    # Pre-lowercase the full text once
    full_text_lower = full_text.lower()

    # Quick check: if no balance keywords exist in the text, keep all currency matches
    has_balance_keywords = any(keyword in full_text_lower for keyword in _BALANCE_KEYWORDS[:5])  # Check only first 5 keywords
    if not has_balance_keywords:
        return matches

    filtered_matches = []

    for text, replacement, start, end, category in matches:
        # Only filter currency category matches
        if category == 'currency':
            if not is_balance_amount_optimized(text, start, full_text, full_text_lower):
                filtered_matches.append((text, replacement, start, end, category))
            # Skip balance amounts (don't add to filtered_matches)
        else:
            # Keep all non-currency matches
            filtered_matches.append((text, replacement, start, end, category))

    return filtered_matches


def is_balance_amount_optimized(text: str, start_pos: int, full_text: str, full_text_lower: str) -> bool:
    """
    Optimized version of is_balance_amount that uses pre-lowercased text.
    """
    # Quick optimization: get smaller context first (50 chars instead of 200)
    context_start = max(0, start_pos - 50)
    before_context = full_text_lower[context_start:start_pos]

    # Quick check with short context first
    for keyword in _BALANCE_KEYWORDS:
        if keyword in before_context:
            return True

    # Only do expensive line-based check if quick check failed
    # Get current line context
    line_start = full_text.rfind('\n', 0, start_pos) + 1

    # Only check line if it's different from what we already checked
    if line_start < context_start:
        line_context = full_text_lower[line_start:start_pos]
        amount_pos_in_line = start_pos - line_start

        for keyword in _BALANCE_KEYWORDS:
            keyword_pos = line_context.find(keyword)
            if keyword_pos != -1 and keyword_pos < amount_pos_in_line:
                return True

    return False


def resolve_overlapping_matches(all_matches: List[Tuple[str, str, int, int, str]]) -> List[Tuple[str, str, int, int, str]]:
    """
    Resolve overlapping pattern matches by priority.

    Args:
        all_matches: List of (text, replacement, start, end, category) tuples

    Returns:
        Filtered list with overlaps resolved by priority
    """
    if not all_matches:
        return all_matches

    priority_order = get_pattern_priority()

    # Sort by priority (lower number = higher priority), then by start position
    sorted_matches = sorted(all_matches, key=lambda x: (priority_order.get(x[4], 999), x[2]))

    resolved_matches = []

    for match in sorted_matches:
        text, replacement, start, end, category = match

        # Check if this match overlaps with any already resolved match
        overlaps = False
        for resolved_text, resolved_replacement, resolved_start, resolved_end, resolved_category in resolved_matches:
            # Check if ranges overlap
            if not (end <= resolved_start or start >= resolved_end):
                overlaps = True
                break

        # If no overlap, add this match
        if not overlaps:
            resolved_matches.append(match)

    # Sort final results by position for consistent output
    return sorted(resolved_matches, key=lambda x: x[2])