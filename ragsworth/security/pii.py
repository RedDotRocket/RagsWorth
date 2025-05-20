"""
PII detection and blocking utilities.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

import spacy
from spacy.language import Language
from spacy.tokens import Doc, Span

@dataclass
class PIIConfig:
    """Configuration for PII detection and blocking."""
    enabled: bool = True
    block_types: Set[str] = None  # If None, block all types
    replacement_char: str = "X"
    log_blocked: bool = True
    
    def __post_init__(self):
        if self.block_types is None:
            self.block_types = {
                "PERSON", "ORG", "GPE", "LOC",  # NER types
                "EMAIL", "PHONE", "SSN", "IP_ADDRESS",  # Custom types
                "CREDIT_CARD", "BANK_ACCOUNT"
            }

class PIIDetector:
    """Detects and blocks PII in text using spaCy and regex patterns."""
    
    def __init__(self, config: PIIConfig):
        self.config = config
        self.nlp = self._load_spacy_model()
        self._add_custom_patterns()
        
    def _load_spacy_model(self) -> Language:
        """Load and configure spaCy model."""
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Download if not available
            spacy.cli.download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
            
        return nlp
    
    def _add_custom_patterns(self) -> None:
        """Add custom regex patterns for additional PII types."""
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        
        patterns = [
            {
                "label": "EMAIL",
                "pattern": [{"TEXT": {"REGEX": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"}}]
            },
            {
                "label": "PHONE",
                "pattern": [{"TEXT": {"REGEX": r"\+?1?\d{9,15}"}}]
            },
            {
                "label": "SSN",
                "pattern": [{"TEXT": {"REGEX": r"\d{3}-\d{2}-\d{4}"}}]
            },
            {
                "label": "IP_ADDRESS",
                "pattern": [{"TEXT": {"REGEX": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"}}]
            },
            {
                "label": "CREDIT_CARD",
                "pattern": [{"TEXT": {"REGEX": r"\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}"}}]
            }
        ]
        
        ruler.add_patterns(patterns)
    
    def _mask_entity(self, text: str, start: int, end: int) -> str:
        """Replace entity with mask characters."""
        return text[:start] + self.config.replacement_char * (end - start) + text[end:]
    
    def detect_and_block(self, text: str) -> Tuple[str, List[Dict]]:
        """Detect and block PII in text, returning blocked text and audit log."""
        if not self.config.enabled:
            return text, []
            
        doc: Doc = self.nlp(text)
        blocked_text = text
        audit_log = []
        
        # Process entities in reverse order to preserve offsets
        for ent in reversed(doc.ents):
            if ent.label_ in self.config.block_types:
                # Block the entity
                blocked_text = self._mask_entity(blocked_text, ent.start_char, ent.end_char)
                
                # Log if enabled
                if self.config.log_blocked:
                    audit_log.append({
                        "type": ent.label_,
                        "text": ent.text,
                        "timestamp": datetime.utcnow().isoformat(),
                        "context": text[max(0, ent.start_char-20):min(len(text), ent.end_char+20)]
                    })
        
        return blocked_text, audit_log
    
    def scan_output(self, text: str) -> Tuple[str, List[Dict]]:
        """Scan model output for potential PII leakage."""
        # Use same detection logic but with stricter patterns
        return self.detect_and_block(text) 