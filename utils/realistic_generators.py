"""
Realistic data generators for redaction replacements.
"""
import random
import hashlib
from typing import Dict, List, Any


class RealisticDataGenerator:
    """Generates realistic-looking replacement data for redaction."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration settings."""
        self.config = config
        self.replacement_settings = config.get("replacement_settings", {})
        self.use_consistent = self.replacement_settings.get("use_consistent_replacements", True)
        self._replacement_cache = {}  # Cache for consistent replacements
        
    def _get_consistent_replacement(self, original_value: str, generator_func) -> str:
        """Get consistent replacement for the same original value."""
        if not self.use_consistent:
            return generator_func()
        
        # Use hash of original value to determine replacement
        if original_value not in self._replacement_cache:
            # Create deterministic seed from original value
            seed_value = int(hashlib.md5(original_value.encode()).hexdigest()[:8], 16)
            random.seed(seed_value)
            self._replacement_cache[original_value] = generator_func()
            random.seed()  # Reset to random seed
        
        return self._replacement_cache[original_value]
    
    def generate_ssn(self, original: str = "") -> str:
        """Generate realistic SSN."""
        def _generate():
            # Use safe ranges that don't represent real SSNs
            area = random.randint(900, 999)  # Invalid SSN area numbers
            group = random.randint(10, 99)
            serial = random.randint(1000, 9999)
            return f"{area}-{group}-{serial}"
        
        if original:
            return self._get_consistent_replacement(original, _generate)
        return _generate()
    
    def generate_phone(self, original: str = "") -> str:
        """Generate realistic phone number."""
        def _generate():
            area_codes = self.replacement_settings.get("phone_area_codes", ["555"])
            area_code = random.choice(area_codes)
            exchange = random.randint(100, 999)
            number = random.randint(1000, 9999)
            return f"({area_code}) {exchange}-{number}"
        
        if original:
            return self._get_consistent_replacement(original, _generate)
        return _generate()
    
    def generate_account_number(self, original: str = "") -> str:
        """Generate realistic account number."""
        def _generate():
            # Generate 10-12 digit account number
            length = random.randint(10, 12)
            return ''.join([str(random.randint(0, 9)) for _ in range(length)])
        
        if original:
            return self._get_consistent_replacement(original, _generate)
        return _generate()
    
    def generate_routing_number(self, original: str = "") -> str:
        """Generate realistic routing number."""
        def _generate():
            # Generate 9-digit routing number starting with valid prefixes
            valid_prefixes = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
            prefix = random.choice(valid_prefixes)
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(7)])
            return prefix + suffix
        
        if original:
            return self._get_consistent_replacement(original, _generate)
        return _generate()
    
    def generate_credit_card(self, original: str = "") -> str:
        """Generate realistic credit card number."""
        def _generate():
            # Use test credit card prefixes that are safe
            test_prefixes = ['4000', '4111', '4222', '5555']  # Test card prefixes
            prefix = random.choice(test_prefixes)
            
            if prefix.startswith('4'):  # Visa-like
                # Generate 16-digit number
                suffix = ''.join([str(random.randint(0, 9)) for _ in range(12)])
                return f"{prefix}-{suffix[:4]}-{suffix[4:8]}-{suffix[8:12]}"
            else:  # Mastercard-like
                suffix = ''.join([str(random.randint(0, 9)) for _ in range(12)])
                return f"{prefix}-{suffix[:4]}-{suffix[4:8]}-{suffix[8:12]}"
        
        if original:
            return self._get_consistent_replacement(original, _generate)
        return _generate()
    
    def generate_tax_id(self, original: str = "") -> str:
        """Generate realistic tax ID/EIN."""
        def _generate():
            # Generate EIN in format XX-XXXXXXX
            prefix = random.randint(10, 99)
            suffix = random.randint(1000000, 9999999)
            return f"{prefix}-{suffix}"
        
        if original:
            return self._get_consistent_replacement(original, _generate)
        return _generate()
    
    def generate_email(self, original: str = "") -> str:
        """Generate realistic email address."""
        def _generate():
            names = self.replacement_settings.get("realistic_names", ["john.doe"])
            domains = self.replacement_settings.get("email_domains", ["example.com"])
            
            # Create username from name
            name = random.choice(names)
            username = name.lower().replace(" ", ".")
            domain = random.choice(domains)
            
            return f"{username}@{domain}"
        
        if original:
            return self._get_consistent_replacement(original, _generate)
        return _generate()
    
    def generate_address(self, original: str = "") -> str:
        """Generate realistic address."""
        def _generate():
            addresses = self.replacement_settings.get("realistic_addresses", {})
            streets = addresses.get("streets", ["123 Main St", "456 Oak Ave", "789 Pine Rd", "321 Elm Dr", "555 Maple Way"])
            cities_states = addresses.get("cities_states", ["Anytown, CA", "Springfield, IL", "Franklin, TX", "Madison, WI"])
            
            # Generate components
            street_num = random.randint(100, 9999)
            street_names = ["MAIN", "OAK", "PINE", "ELM", "MAPLE", "CEDAR", "PARK", "FIRST", "SECOND", "THIRD"]
            street_types = ["ST", "AVE", "RD", "DR", "WAY", "LN", "BLVD", "CT", "PL"]
            
            street_name = random.choice(street_names)
            street_type = random.choice(street_types)
            
            # Check original format to match
            if any(x in original.upper() for x in ["ST", "STREET", "AVE", "AVENUE", "RD", "ROAD"]):
                # Street address format
                return f"{street_num} {street_name} {street_type}"
            elif any(x in original for x in [","]) and any(x in original for x in ["CA", "TX", "NY", "FL"]):
                # City, State ZIP format
                city_state = random.choice(cities_states)
                zip_code = random.randint(10000, 99999)
                if "-" in original:
                    zip_ext = random.randint(1000, 9999)
                    return f"{city_state} {zip_code}-{zip_ext}"
                else:
                    return f"{city_state} {zip_code}"
            else:
                # Default full address
                city_state = random.choice(cities_states)
                zip_code = random.randint(10000, 99999)
                return f"{street_num} {street_name} {street_type}"
        
        if original:
            return self._get_consistent_replacement(original, _generate)
        return _generate()
    
    def generate_employer_name(self, original: str = "") -> str:
        """Generate realistic employer name."""
        def _generate():
            companies = self.replacement_settings.get("realistic_companies", ["ACME Corp"])
            return random.choice(companies)
        
        if original:
            return self._get_consistent_replacement(original, _generate)
        return _generate()
    
    def generate_currency(self, original: str = "") -> str:
        """Generate realistic currency amount."""
        def _generate():
            # Generate amount between $10 and $10,000
            amount = random.uniform(10, 10000)
            return f"${amount:,.2f}"
        
        if original:
            return self._get_consistent_replacement(original, _generate)
        return _generate()
    
    def generate_date(self, original: str = "") -> str:
        """Generate realistic date."""
        def _generate():
            month = random.randint(1, 12)
            day = random.randint(1, 28)  # Safe day range
            year = random.randint(2020, 2024)
            
            # Match format of original if possible
            if "/" in original:
                return f"{month:02d}/{day:02d}/{year}"
            elif "-" in original:
                return f"{month:02d}-{day:02d}-{year}"
            else:
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                return f"{months[month-1]} {day}, {year}"
        
        if original:
            return self._get_consistent_replacement(original, _generate)
        return _generate()
    
    def generate_person_name(self, original: str = "") -> str:
        """Generate realistic person name with matching length."""
        def _generate():
            if not original.strip():
                # No original provided, use default generation
                return self._generate_default_name()
            
            # Try to match the original name's length
            return self._generate_length_matched_name(original)
        
        if original:
            return self._get_consistent_replacement(original, _generate)
        return _generate()
    
    def _generate_default_name(self) -> str:
        """Generate default name without length constraints."""
        # Get names from config or use defaults
        first_names_male = self.replacement_settings.get("realistic_first_names_male", 
            ["John", "Michael", "David", "James", "Robert", "William", "Christopher", "Matthew"])
        first_names_female = self.replacement_settings.get("realistic_first_names_female",
            ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica"])
        last_names = self.replacement_settings.get("realistic_last_names",
            ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"])
        
        # Combine male and female names
        all_first_names = first_names_male + first_names_female
        
        # Generate name
        first_name = random.choice(all_first_names)
        last_name = random.choice(last_names)
        return f"{first_name} {last_name}"
    
    def _generate_length_matched_name(self, original: str) -> str:
        """Generate name that matches the original length as closely as possible."""
        original_len = len(original)
        original_words = original.strip().split()
        
        # Get name lists
        first_names_male = self.replacement_settings.get("realistic_first_names_male", 
            ["John", "Michael", "David", "James", "Robert", "William", "Christopher", "Matthew", "Dan", "Tom", "Sam", "Jim"])
        first_names_female = self.replacement_settings.get("realistic_first_names_female",
            ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Ann", "Sue", "Kim", "Amy"])
        last_names = self.replacement_settings.get("realistic_last_names",
            ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Lee", "Wu", "Li", "Chen"])
        
        all_first_names = first_names_male + first_names_female
        
        # Handle titles if present
        title_prefix = ""
        if any(title in original.lower() for title in ["mr.", "ms.", "mrs.", "dr.", "prof."]):
            titles = ["Mr.", "Ms.", "Mrs.", "Dr."]
            title_prefix = random.choice(titles) + " "
            original_len -= len(title_prefix)
        
        best_match = ""
        best_diff = float('inf')
        
        # Try different combinations to match length
        for _ in range(50):  # Try up to 50 combinations
            if len(original_words) >= 3:
                # Try with middle initial
                first = random.choice(all_first_names)
                last = random.choice(last_names)
                middle = random.choice("ABCDEFGHJKLM")
                candidate = f"{first} {middle}. {last}"
            else:
                # Try first + last combination
                first = random.choice(all_first_names)
                last = random.choice(last_names)
                candidate = f"{first} {last}"
            
            candidate_len = len(candidate)
            diff = abs(candidate_len - original_len)
            
            if diff < best_diff:
                best_diff = diff
                best_match = candidate
                
            # If we found exact match, use it
            if diff == 0:
                break
        
        # If no good match found and original is very short/long, try alternatives
        if best_diff > 3:
            if original_len <= 8:
                # Very short - try short names
                short_firsts = [name for name in all_first_names if len(name) <= 4]
                short_lasts = [name for name in last_names if len(name) <= 5]
                if short_firsts and short_lasts:
                    best_match = f"{random.choice(short_firsts)} {random.choice(short_lasts)}"
            elif original_len >= 20:
                # Very long - try long names with middle name
                long_firsts = [name for name in all_first_names if len(name) >= 7]
                long_lasts = [name for name in last_names if len(name) >= 7]
                if long_firsts and long_lasts:
                    best_match = f"{random.choice(long_firsts)} {random.choice('ABCDEFGHJKLM')}. {random.choice(long_lasts)}"
        
        return title_prefix + best_match
    
    def clear_cache(self):
        """Clear the replacement cache."""
        self._replacement_cache.clear()