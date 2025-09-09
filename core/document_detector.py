"""
Document type detection for financial documents.
"""
from typing import List, Dict


class DocumentTypeDetector:
    """Handles detection of financial document types based on content analysis."""
    
    def __init__(self):
        """Initialize the detector with predefined keyword sets."""
        self.detection_rules = self._get_detection_rules()
    
    def _get_detection_rules(self) -> Dict[str, Dict[str, any]]:
        """Define detection rules for different document types."""
        return {
            'bank_statement': {
                'keywords': [
                    'account summary', 'checking account', 'savings account', 'statement period',
                    'beginning balance', 'ending balance', 'deposits', 'withdrawals', 'bank'
                ],
                'threshold': 3
            },
            'w2': {
                'keywords': [
                    'wage and tax statement', 'employer identification number', 'ein',
                    'federal income tax withheld', 'social security wages', 'medicare wages'
                ],
                'threshold': 2
            },
            'tax_return': {
                'keywords': [
                    'form 1040', 'adjusted gross income', 'taxable income', 'tax return',
                    'irs', 'schedule', 'itemized deductions', 'standard deduction'
                ],
                'threshold': 2
            },
            'pay_stub': {
                'keywords': [
                    'pay stub', 'payroll', 'gross pay', 'net pay', 'year to date',
                    'ytd', 'deductions', 'hours worked', 'pay period'
                ],
                'threshold': 2
            }
        }
    
    def detect_document_type(self, text: str) -> str:
        """
        Detect the type of financial document based on content.
        
        Args:
            text: Document text content to analyze
            
        Returns:
            Document type string: 'bank_statement', 'w2', 'tax_return', 'pay_stub', or 'general'
        """
        text_lower = text.lower()
        
        for doc_type, rules in self.detection_rules.items():
            keyword_count = sum(1 for keyword in rules['keywords'] if keyword in text_lower)
            if keyword_count >= rules['threshold']:
                return doc_type
        
        return 'general'
    
    def get_detection_confidence(self, text: str, doc_type: str = None) -> Dict[str, float]:
        """
        Get confidence scores for document type detection.
        
        Args:
            text: Document text content
            doc_type: Optional specific document type to check
            
        Returns:
            Dictionary mapping document types to confidence scores (0.0-1.0)
        """
        text_lower = text.lower()
        confidence_scores = {}
        
        types_to_check = [doc_type] if doc_type else self.detection_rules.keys()
        
        for dt in types_to_check:
            if dt in self.detection_rules:
                rules = self.detection_rules[dt]
                keyword_matches = sum(1 for keyword in rules['keywords'] if keyword in text_lower)
                confidence = min(keyword_matches / rules['threshold'], 1.0)
                confidence_scores[dt] = confidence
        
        return confidence_scores
    
    def add_detection_rule(self, doc_type: str, keywords: List[str], threshold: int = 2):
        """
        Add a new document type detection rule.
        
        Args:
            doc_type: Name of the document type
            keywords: List of keywords to look for
            threshold: Minimum number of keywords required for detection
        """
        self.detection_rules[doc_type] = {
            'keywords': keywords,
            'threshold': threshold
        }
    
    def get_supported_types(self) -> List[str]:
        """Get list of supported document types."""
        return list(self.detection_rules.keys())