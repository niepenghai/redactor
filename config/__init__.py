"""Configuration management and pattern definitions."""

from .manager import ConfigurationManager
from .patterns import get_financial_patterns, get_patterns_for_document_type

__all__ = [
    "ConfigurationManager",
    "get_financial_patterns",
    "get_patterns_for_document_type"
]