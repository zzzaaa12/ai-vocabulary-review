"""
English words suggestion service.
Provides autocomplete suggestions from a large English dictionary.

Word data source: dwyl/english-words project (https://github.com/dwyl/english-words)
License: Unlicense (Public Domain)
Contains 370,000+ English words for autocomplete functionality.
"""

import os
from typing import List, Dict, Any
import bisect


class EnglishWordsService:
    """
    Service for providing English word suggestions from the dwyl/english-words dataset.
    """

    def __init__(self, words_file_path: str = "words_alpha.txt"):
        """
        Initialize the English words service.

        Args:
            words_file_path: Path to the words file
        """
        self.words_file_path = words_file_path
        self._words = []
        self._loaded = False

    def _load_words(self) -> None:
        """
        Load words from file into memory (lazy loading).
        """
        if self._loaded:
            return

        if not os.path.exists(self.words_file_path):
            print(f"Warning: English words file not found at {self.words_file_path}")
            self._words = []
            self._loaded = True
            return

        try:
            with open(self.words_file_path, 'r', encoding='utf-8') as f:
                self._words = [line.strip().lower() for line in f if line.strip()]

            # Sort words for binary search optimization
            self._words.sort()
            self._loaded = True
            print(f"Loaded {len(self._words)} English words")

        except Exception as e:
            print(f"Error loading English words: {e}")
            self._words = []
            self._loaded = True

    def get_suggestions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get English word suggestions for autocomplete.

        Args:
            query: Search query
            limit: Maximum number of suggestions to return

        Returns:
            List of suggestion dictionaries
        """
        if not query or len(query) < 2:
            return []

        self._load_words()

        if not self._words:
            return []

        query_lower = query.lower()
        suggestions = []

        # Find words that start with the query using binary search
        start_index = bisect.bisect_left(self._words, query_lower)

        # Collect words that start with the query
        for i in range(start_index, min(start_index + limit * 2, len(self._words))):
            word = self._words[i]
            if word.startswith(query_lower):
                suggestions.append({
                    'word': word,
                    'display_text': word,
                    'match_type': 'starts_with',
                    'source': 'english_dictionary'
                })

                if len(suggestions) >= limit:
                    break
            else:
                # Since words are sorted, we can break when we no longer find matches
                break

        return suggestions

    def is_valid_word(self, word: str) -> bool:
        """
        Check if a word exists in the English dictionary.

        Args:
            word: Word to check

        Returns:
            True if word exists in dictionary
        """
        if not word:
            return False

        self._load_words()

        if not self._words:
            return False

        return word.lower() in self._words

    def get_word_count(self) -> int:
        """
        Get total number of words in the dictionary.

        Returns:
            Number of words
        """
        self._load_words()
        return len(self._words)
