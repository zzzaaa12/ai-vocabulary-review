"""
Vocabulary service for managing word data operations.
This service handles CRUD operations and business logic for vocabulary management.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os

from models.vocabulary import Word, VocabularyData


class VocabularyService:
    """
    Service class for managing vocabulary data operations.
    Handles file I/O, CRUD operations, and business logic.
    """
    
    def __init__(self, data_file_path: str):
        """
        Initialize the vocabulary service.
        
        Args:
            data_file_path: Path to the JSON data file
        """
        self.data_file_path = data_file_path
        self._ensure_data_file_exists()
    
    def _ensure_data_file_exists(self) -> None:
        """
        Ensure the data file exists, create empty one if it doesn't.
        """
        if not os.path.exists(self.data_file_path):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.data_file_path), exist_ok=True)
            
            # Create empty vocabulary data file
            empty_data = VocabularyData()
            self._save_data(empty_data)
    
    def _load_data(self) -> VocabularyData:
        """
        Load vocabulary data from JSON file.
        
        Returns:
            VocabularyData instance
            
        Raises:
            FileNotFoundError: If data file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    # Empty file, return empty data
                    return VocabularyData()
                data = json.loads(content)
                return VocabularyData.from_dict(data)
        except FileNotFoundError:
            # Return empty data if file doesn't exist
            return VocabularyData()
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in data file: {e}")
    
    def _save_data(self, vocab_data: VocabularyData) -> None:
        """
        Save vocabulary data to JSON file.
        
        Args:
            vocab_data: VocabularyData instance to save
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            with open(self.data_file_path, 'w', encoding='utf-8') as f:
                json.dump(vocab_data.to_dict(), f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise IOError(f"Cannot write to data file: {e}")
    
    def get_all_words(self) -> List[Word]:
        """
        Get all vocabulary words.
        
        Returns:
            List of Word instances
        """
        vocab_data = self._load_data()
        return vocab_data.vocabulary
    
    def get_word_by_id(self, word_id: str) -> Optional[Word]:
        """
        Get a specific word by its ID.
        
        Args:
            word_id: Unique identifier for the word
            
        Returns:
            Word instance if found, None otherwise
        """
        vocab_data = self._load_data()
        return vocab_data.find_word_by_id(word_id)
    
    def add_word(self, word: Word) -> Word:
        """
        Add a new word to the vocabulary.
        
        Args:
            word: Word instance to add
            
        Returns:
            The added Word instance
            
        Raises:
            ValueError: If word validation fails
        """
        # Validate word data
        validation_errors = word.validate()
        if validation_errors:
            raise ValueError(f"Word validation failed: {', '.join(validation_errors)}")
        
        # Check for duplicate words
        if self.word_exists(word.word):
            raise ValueError(f"Word '{word.word}' already exists")
        
        # Load current data, add word, and save
        vocab_data = self._load_data()
        vocab_data.add_word(word)
        self._save_data(vocab_data)
        
        return word
    
    def update_word(self, word_id: str, **kwargs) -> Optional[Word]:
        """
        Update an existing word.
        
        Args:
            word_id: ID of the word to update
            **kwargs: Fields to update
            
        Returns:
            Updated Word instance if found, None otherwise
            
        Raises:
            ValueError: If validation fails
        """
        vocab_data = self._load_data()
        word = vocab_data.find_word_by_id(word_id)
        
        if not word:
            return None
        
        # Update fields
        word.update_fields(**kwargs)
        
        # Validate updated word
        validation_errors = word.validate()
        if validation_errors:
            raise ValueError(f"Word validation failed: {', '.join(validation_errors)}")
        
        # Save updated data
        self._save_data(vocab_data)
        
        return word
    
    def delete_word(self, word_id: str) -> bool:
        """
        Delete a word by its ID.
        
        Args:
            word_id: ID of the word to delete
            
        Returns:
            True if word was deleted, False if not found
        """
        vocab_data = self._load_data()
        success = vocab_data.remove_word(word_id)
        
        if success:
            self._save_data(vocab_data)
        
        return success
    
    def word_exists(self, word: str) -> bool:
        """
        Check if a word already exists in the vocabulary.
        
        Args:
            word: The word to check
            
        Returns:
            True if word exists, False otherwise
        """
        vocab_data = self._load_data()
        return any(w.word.lower() == word.lower() for w in vocab_data.vocabulary)
    
    def search_words(self, query: str) -> List[Word]:
        """
        Search for words matching the query.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching Word instances
        """
        if not query.strip():
            return []
        
        vocab_data = self._load_data()
        query_lower = query.lower()
        
        matching_words = []
        for word in vocab_data.vocabulary:
            # Search in word, Chinese meaning, and English meaning
            if (query_lower in word.word.lower() or 
                query_lower in word.chinese_meaning.lower() or 
                query_lower in word.english_meaning.lower()):
                matching_words.append(word)
        
        return matching_words
    
    def get_words_by_time_filter(self, time_filter: str) -> List[Word]:
        """
        Get words filtered by time range.
        
        Args:
            time_filter: Time filter ('recent_2_days', 'recent_week', 'recent_2_weeks', 'recent_month')
            
        Returns:
            List of Word instances within the time range
        """
        TIME_FILTERS = {
            'recent_2_days': 2,
            'recent_week': 7,
            'recent_2_weeks': 14,
            'recent_month': 30
        }
        
        if time_filter not in TIME_FILTERS:
            return self.get_all_words()
        
        days = TIME_FILTERS[time_filter]
        cutoff_date = datetime.now() - timedelta(days=days)
        
        vocab_data = self._load_data()
        filtered_words = [
            word for word in vocab_data.vocabulary 
            if word.created_date >= cutoff_date
        ]
        
        # Sort by creation date (newest first)
        filtered_words.sort(key=lambda w: w.created_date, reverse=True)
        
        return filtered_words
    
    def get_total_word_count(self) -> int:
        """
        Get the total number of words in the vocabulary.
        
        Returns:
            Total word count
        """
        vocab_data = self._load_data()
        return len(vocab_data.vocabulary)