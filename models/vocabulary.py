"""
Core vocabulary data model for the English vocabulary notebook application.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid


class Word:
    """
    Core Word model representing a vocabulary entry.
    """
    
    def __init__(
        self,
        word: str,
        chinese_meaning: str,
        english_meaning: str = "",
        phonetic: str = "",
        example_sentence: str = "",
        synonyms: Optional[List[str]] = None,
        antonyms: Optional[List[str]] = None,
        word_id: Optional[str] = None
    ):
        """
        Initialize a Word instance.
        
        Args:
            word: The English word
            chinese_meaning: Chinese translation/meaning
            english_meaning: English definition
            phonetic: Phonetic transcription
            example_sentence: Example usage sentence
            synonyms: List of synonymous words
            antonyms: List of antonymous words
            word_id: Unique identifier (auto-generated if not provided)
        """
        self.id = word_id or str(uuid.uuid4())
        self.word = word.strip()
        self.chinese_meaning = chinese_meaning.strip()
        self.english_meaning = english_meaning.strip()
        self.phonetic = phonetic.strip()
        self.example_sentence = example_sentence.strip()
        self.synonyms = synonyms or []
        self.antonyms = antonyms or []
        self.created_date = datetime.now()
        self.updated_date = datetime.now()
    
    def validate(self) -> List[str]:
        """
        Validate the word data and return list of validation errors.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        if not self.word:
            errors.append("英文單字不能為空")
        
        if not self.chinese_meaning:
            errors.append("中文解釋不能為空")
        
        if len(self.word) > 100:
            errors.append("英文單字長度不能超過100個字符")
        
        if len(self.chinese_meaning) > 200:
            errors.append("中文解釋長度不能超過200個字符")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Word instance to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the word
        """
        return {
            "id": self.id,
            "word": self.word,
            "chinese_meaning": self.chinese_meaning,
            "english_meaning": self.english_meaning,
            "phonetic": self.phonetic,
            "example_sentence": self.example_sentence,
            "synonyms": self.synonyms,
            "antonyms": self.antonyms,
            "created_date": self.created_date.isoformat(),
            "updated_date": self.updated_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Word':
        """
        Create Word instance from dictionary data.
        
        Args:
            data: Dictionary containing word data
            
        Returns:
            Word instance
        """
        word = cls(
            word=data.get("word", ""),
            chinese_meaning=data.get("chinese_meaning", ""),
            english_meaning=data.get("english_meaning", ""),
            phonetic=data.get("phonetic", ""),
            example_sentence=data.get("example_sentence", ""),
            synonyms=data.get("synonyms", []),
            antonyms=data.get("antonyms", []),
            word_id=data.get("id")
        )
        
        # Parse dates if available
        if "created_date" in data:
            try:
                word.created_date = datetime.fromisoformat(data["created_date"])
            except (ValueError, TypeError):
                pass
        
        if "updated_date" in data:
            try:
                word.updated_date = datetime.fromisoformat(data["updated_date"])
            except (ValueError, TypeError):
                pass
        
        return word
    
    def update_fields(self, **kwargs) -> None:
        """
        Update word fields and set updated_date.
        
        Args:
            **kwargs: Fields to update
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_date = datetime.now()
    
    def __str__(self) -> str:
        return f"{self.word} - {self.chinese_meaning}"
    
    def __repr__(self) -> str:
        return f"Word(id='{self.id}', word='{self.word}', chinese_meaning='{self.chinese_meaning}')"


class VocabularyData:
    """
    Container class for vocabulary data with metadata.
    """
    
    def __init__(self):
        self.vocabulary: List[Word] = []
        self.metadata = {
            "total_words": 0,
            "last_updated": datetime.now().isoformat()
        }
    
    def add_word(self, word: Word) -> None:
        """Add a word to the vocabulary list."""
        self.vocabulary.append(word)
        self.update_metadata()
    
    def remove_word(self, word_id: str) -> bool:
        """
        Remove a word by ID.
        
        Returns:
            True if word was removed, False if not found
        """
        for i, word in enumerate(self.vocabulary):
            if word.id == word_id:
                del self.vocabulary[i]
                self.update_metadata()
                return True
        return False
    
    def find_word_by_id(self, word_id: str) -> Optional[Word]:
        """Find a word by its ID."""
        for word in self.vocabulary:
            if word.id == word_id:
                return word
        return None
    
    def update_metadata(self) -> None:
        """Update metadata information."""
        self.metadata["total_words"] = len(self.vocabulary)
        self.metadata["last_updated"] = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "vocabulary": [word.to_dict() for word in self.vocabulary],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VocabularyData':
        """Create VocabularyData from dictionary."""
        vocab_data = cls()
        
        # Load vocabulary words
        for word_data in data.get("vocabulary", []):
            word = Word.from_dict(word_data)
            vocab_data.vocabulary.append(word)
        
        # Load metadata
        vocab_data.metadata = data.get("metadata", vocab_data.metadata)
        
        return vocab_data