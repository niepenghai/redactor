"""
Configuration management for the financial document redactor.
"""
import json
import os
from typing import Dict, Any, Optional


class ConfigurationManager:
    """Handles loading, saving, and managing configuration settings."""
    
    def __init__(self, base_dir: str):
        """
        Initialize the configuration manager.
        
        Args:
            base_dir: Base directory for configuration files
        """
        self.base_dir = base_dir
        self.config_path = os.path.join(base_dir, "config.json")
        self.default_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get the default configuration settings."""
        return {
            "redaction_level": "standard",  # minimal, standard, aggressive
            "replacement_mode": "generic",  # generic, realistic, custom
            "enabled_categories": {
                "ssn": True,
                "phone": True,
                "account_number": True,
                "routing_number": True,
                "credit_card": True,
                "tax_id": True,
                "currency": False,  # Often users want to see amounts
                "dates": False,     # Often needed for document context
                "email": True,
                "address": True,
                "employer": False,   # Sometimes needed for document context
                "names": True       # Personal names redaction
            },
            "replacement_settings": {
                "use_consistent_replacements": True,  # Use same replacement for identical values
                "realistic_names": ["John Smith", "Jane Doe", "Michael Johnson", "Sarah Williams"],
                "realistic_companies": ["ACME Corp", "Global Industries", "Tech Solutions Inc", "Business Services LLC"],
                "realistic_addresses": {
                    "streets": ["123 Main St", "456 Oak Ave", "789 Pine Rd", "321 Elm Dr"],
                    "cities_states": ["Anytown, CA", "Springfield, IL", "Franklin, TX", "Madison, WI"]
                },
                "phone_area_codes": ["555", "444", "333"],  # Safe fake area codes
                "email_domains": ["example.com", "test.org", "sample.net"],
                "realistic_first_names_male": ["John", "Michael", "David", "James", "Robert", "William", "Christopher", "Matthew", "Daniel", "Thomas"],
                "realistic_first_names_female": ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"],
                "realistic_last_names": ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez"]
            },
            "custom_patterns": [],
            "custom_strings": [],
            "output_settings": {
                "preserve_formatting": True,
                "add_watermark": False,
                "compression_level": "medium"
            },
            "logging": {
                "enabled": True,
                "level": "INFO",
                "log_file": "redactor.log"
            }
        }
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from file or create default.
        
        Args:
            config_path: Optional custom path to config file
            
        Returns:
            Configuration dictionary
        """
        path = config_path or self.config_path
        
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._merge_with_defaults(config)
            else:
                # Create default config file
                self.save_config(self.default_config, path)
                print(f"📄 Created config.json with default settings")
                return self.default_config.copy()
        except Exception as e:
            print(f"⚠️  Error loading config from {path}, using defaults: {str(e)}")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any], config_path: Optional[str] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            config_path: Optional custom path to save to
            
        Returns:
            True if successful, False otherwise
        """
        path = config_path or self.config_path
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"⚠️  Error saving config to {path}: {str(e)}")
            return False
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge loaded config with defaults to ensure all keys exist.
        
        Args:
            config: Loaded configuration
            
        Returns:
            Merged configuration with all default keys
        """
        merged = self.default_config.copy()
        
        # Recursively merge nested dictionaries
        def deep_merge(default: Dict, loaded: Dict) -> Dict:
            result = default.copy()
            for key, value in loaded.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(merged, config)
    
    def update_config(self, updates: Dict[str, Any], save: bool = True) -> Dict[str, Any]:
        """
        Update configuration with new values.
        
        Args:
            updates: Dictionary of updates to apply
            save: Whether to save changes to file
            
        Returns:
            Updated configuration
        """
        current_config = self.load_config()
        
        # Apply updates
        def apply_updates(config: Dict, updates: Dict):
            for key, value in updates.items():
                if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                    apply_updates(config[key], value)
                else:
                    config[key] = value
        
        apply_updates(current_config, updates)
        
        if save:
            self.save_config(current_config)
        
        return current_config
    
    def validate_config(self, config: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate configuration settings.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate redaction level
        valid_levels = ["minimal", "standard", "aggressive"]
        if config.get("redaction_level") not in valid_levels:
            errors.append(f"Invalid redaction_level. Must be one of: {valid_levels}")
        
        # Validate enabled_categories
        if "enabled_categories" in config:
            if not isinstance(config["enabled_categories"], dict):
                errors.append("enabled_categories must be a dictionary")
            else:
                for key, value in config["enabled_categories"].items():
                    if not isinstance(value, bool):
                        errors.append(f"enabled_categories.{key} must be boolean")
        
        # Validate custom_patterns
        if "custom_patterns" in config:
            if not isinstance(config["custom_patterns"], list):
                errors.append("custom_patterns must be a list")
            else:
                for i, pattern in enumerate(config["custom_patterns"]):
                    if not isinstance(pattern, dict):
                        errors.append(f"custom_patterns[{i}] must be a dictionary")
                    elif "pattern" not in pattern or "replacement" not in pattern:
                        errors.append(f"custom_patterns[{i}] must have 'pattern' and 'replacement' keys")
        
        return len(errors) == 0, errors
    
    def get_enabled_categories(self, config: Dict[str, Any]) -> Dict[str, bool]:
        """Get enabled categories from config."""
        return config.get("enabled_categories", self.default_config["enabled_categories"])
    
    def get_custom_patterns(self, config: Dict[str, Any]) -> list:
        """Get custom patterns from config."""
        return config.get("custom_patterns", [])

    def get_custom_strings(self, config: Dict[str, Any]) -> list:
        """Get custom strings from config."""
        return config.get("custom_strings", [])