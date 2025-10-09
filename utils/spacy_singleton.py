"""
Singleton pattern for spaCy model loading.
Ensures only one spaCy model is loaded across the entire application.
"""


class SpaCyModelSingleton:
    """Singleton class to manage spaCy model loading."""

    _instance = None
    _nlp = None
    _loaded = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_model(self):
        """
        Get the spaCy model, loading it if necessary.

        Returns:
            spaCy nlp object or None if not available
        """
        if not self._loaded:
            self._load_model()
            self._loaded = True

        return self._nlp

    def _load_model(self):
        """Load spaCy model once."""
        try:
            import spacy
            try:
                self._nlp = spacy.load("en_core_web_sm")
                print("✅ Loaded spaCy model (singleton)")
            except OSError:
                print("⚠️ spaCy model not found, will use pattern-only detection")
                self._nlp = None
        except ImportError:
            print("⚠️ spaCy not available, will use pattern-only detection")
            self._nlp = None


# Global function for easy access
def get_spacy_model():
    """
    Get the shared spaCy model instance.

    Returns:
        spaCy nlp object or None if not available
    """
    singleton = SpaCyModelSingleton()
    return singleton.get_model()
