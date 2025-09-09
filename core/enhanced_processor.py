"""
Enhanced PDF processor with detailed redaction reporting and realistic data generation.
"""

import os
import re
import fitz  # PyMuPDF
from typing import Dict, List, Tuple, Any

try:
    from ..utils.realistic_generators import RealisticDataGenerator
    from ..config.patterns import get_financial_patterns, enhance_patterns_with_nlp, resolve_overlapping_matches
    from .document_detector import DocumentTypeDetector
except ImportError:
    from utils.realistic_generators import RealisticDataGenerator
    from config.patterns import get_financial_patterns, enhance_patterns_with_nlp, resolve_overlapping_matches
    from core.document_detector import DocumentTypeDetector


class EnhancedPDFProcessor:
    """Enhanced PDF processor with realistic data and detailed reporting."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.realistic_generator = RealisticDataGenerator(config)
        self.document_detector = DocumentTypeDetector()
        
    def get_realistic_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """Get patterns with realistic replacements instead of generic ones."""
        patterns = get_financial_patterns()
        
        # Create realistic replacement versions
        realistic_patterns = {}
        
        for category, pattern_list in patterns.items():
            realistic_patterns[category] = []
            for pattern, _ in pattern_list:  # Ignore generic replacement
                # Use placeholder for now - will be replaced with actual realistic data
                realistic_patterns[category].append((pattern, f"REALISTIC_{category.upper()}"))
        
        return realistic_patterns
    
    def generate_realistic_replacement(self, category: str, original_text: str) -> str:
        """Generate realistic replacement based on category."""
        if category == 'ssn':
            return self.realistic_generator.generate_ssn(original_text)
        elif category == 'phone':
            return self.realistic_generator.generate_phone(original_text)
        elif category == 'names':
            return self.realistic_generator.generate_person_name(original_text)
        elif category == 'email':
            return self.realistic_generator.generate_email(original_text)
        elif category == 'address':
            return self.realistic_generator.generate_address(original_text)
        elif category == 'account_number':
            return self.realistic_generator.generate_account_number(original_text)
        elif category == 'routing_number':
            return self.realistic_generator.generate_routing_number(original_text)
        elif category == 'credit_card':
            return self.realistic_generator.generate_credit_card(original_text)
        elif category == 'tax_id':
            return self.realistic_generator.generate_tax_id(original_text)
        elif category == 'currency':
            return self.realistic_generator.generate_currency(original_text)
        elif category == 'dates':
            return self.realistic_generator.generate_date(original_text)
        else:
            # Fallback to generic replacement
            return f"[{category.upper()}]"
    
    def process_pdf_with_reporting(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        Process PDF with detailed redaction reporting.
        Returns dict with processing results and redaction details.
        """
        try:
            # Open PDF
            doc = fitz.open(input_path)
            
            # Extract text for document type detection
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            
            # Detect document type
            doc_type = self.document_detector.detect_document_type(full_text)
            
            # Get patterns based on configuration and replacement mode
            if self.config.get("replacement_mode") == "realistic":
                base_patterns = get_financial_patterns()
                patterns = enhance_patterns_with_nlp(base_patterns, full_text)
                # Convert to realistic patterns format
                realistic_patterns = {}
                for category, pattern_list in patterns.items():
                    realistic_patterns[category] = []
                    for pattern, _ in pattern_list:
                        realistic_patterns[category].append((pattern, f"REALISTIC_{category.upper()}"))
                patterns = realistic_patterns
            else:
                base_patterns = get_financial_patterns()
                patterns = enhance_patterns_with_nlp(base_patterns, full_text)
            
            # Filter patterns based on enabled categories
            enabled_categories = self.config.get("enabled_categories", {})
            active_patterns = {}
            for category, pattern_list in patterns.items():
                if enabled_categories.get(category, True):  # Default enabled if not specified
                    active_patterns[category] = pattern_list
            
            # Track all redactions
            redaction_report = {
                'document_type': doc_type,
                'total_redactions': 0,
                'redactions_by_category': {},
                'detailed_redactions': []
            }
            
            # Process each page
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_text = page.get_text()
                
                # Collect all matches from all patterns first
                all_matches = []
                
                for category, pattern_list in active_patterns.items():
                    for pattern, generic_replacement in pattern_list:
                        # Find all matches
                        matches = list(re.finditer(pattern, page_text, re.IGNORECASE))
                        
                        for match in matches:
                            original_text = match.group()
                            
                            # Generate realistic or use generic replacement
                            if self.config.get("replacement_mode") == "realistic":
                                replacement_text = self.generate_realistic_replacement(category, original_text)
                            elif self.config.get("replacement_mode") == "custom":
                                custom_replacements = self.config.get("replacement_settings", {}).get("custom_replacements", {})
                                replacement_text = custom_replacements.get(category, generic_replacement)
                            else:
                                replacement_text = generic_replacement
                            
                            # Add to all matches (text, replacement, start, end, category)
                            all_matches.append((original_text, replacement_text, match.start(), match.end(), category))
                
                # Resolve overlapping matches by priority
                resolved_matches = resolve_overlapping_matches(all_matches)
                
                # Apply redactions for resolved matches only
                category_counts = {}
                replacement_insertions = []  # Store positions for replacement text insertion
                
                for original_text, replacement_text, start_pos, end_pos, category in resolved_matches:
                    # Find text instances on the page
                    text_instances = page.search_for(original_text)
                    
                    for inst in text_instances:
                        # Create redaction annotation without replacement text to avoid layout issues
                        redact_annot = page.add_redact_annot(inst, fill=(1, 1, 1))  # White background, no text
                        
                        # Store position for replacement text insertion after redaction
                        replacement_insertions.append((inst, replacement_text))
                        
                        # Record redaction details
                        redaction_detail = {
                            'page': page_num + 1,
                            'category': category,
                            'original': original_text,
                            'replacement': replacement_text,
                            'position': {'x0': inst.x0, 'y0': inst.y0, 'x1': inst.x1, 'y1': inst.y1}
                        }
                        
                        redaction_report['detailed_redactions'].append(redaction_detail)
                        category_counts[category] = category_counts.get(category, 0) + 1
                        redaction_report['total_redactions'] += 1
                
                # Update redactions by category
                for category, count in category_counts.items():
                    redaction_report['redactions_by_category'][category] = redaction_report['redactions_by_category'].get(category, 0) + count
                
                # Apply redactions first
                page.apply_redactions()
                
                # Then insert replacement text at the redacted positions
                for inst, replacement_text in replacement_insertions:
                    # Calculate font size based on the original text box height
                    font_size = min(12, inst.y1 - inst.y0 - 2)  # Leave some padding
                    if font_size < 6:
                        font_size = 8  # Minimum readable font size
                    
                    # Insert replacement text at the position of the original text
                    page.insert_text((inst.x0, inst.y0 + font_size), replacement_text, 
                                    fontsize=font_size, color=(0, 0, 0))  # Black text
            
            # Save the redacted PDF
            doc.save(output_path)
            doc.close()
            
            return {
                'success': True,
                'input_file': os.path.basename(input_path),
                'output_file': os.path.basename(output_path),
                'redaction_report': redaction_report
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'input_file': os.path.basename(input_path) if 'input_path' in locals() else 'unknown'
            }