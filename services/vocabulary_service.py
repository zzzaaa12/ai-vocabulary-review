"""
Vocabulary service for managing word data operations.
This service handles CRUD operations and business logic for vocabulary management.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import os

from models.vocabulary import Word, VocabularyData

# Time filter constants
TIME_FILTERS = {
    'recent_3_days': 3,
    'recent_week': 7,
    'recent_2_weeks': 14,
    'recent_month': 30,
    'recent_3_months': 90,
    'all': None  # Show all words
}

TIME_FILTER_LABELS = {
    'recent_3_days': '近三天',
    'recent_week': '近一週',
    'recent_2_weeks': '近兩週',
    'recent_month': '近一個月',
    'recent_3_months': '近三個月',
    'all': '全部'
}


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

    def add_words_batch(self, words: List[Word]) -> Dict[str, Any]:
        """
        Add multiple words to the vocabulary in batch.

        Args:
            words: List of Word instances to add

        Returns:
            Dictionary with batch operation results:
            {
                'success_count': int,
                'error_count': int,
                'total_count': int,
                'successful_words': List[Word],
                'failed_words': List[Dict],
                'duplicate_words': List[str]
            }
        """
        if not words:
            return {
                'success_count': 0,
                'error_count': 0,
                'total_count': 0,
                'successful_words': [],
                'failed_words': [],
                'duplicate_words': []
            }

        vocab_data = self._load_data()
        successful_words = []
        failed_words = []
        duplicate_words = []

        for word in words:
            try:
                # Validate word data
                validation_errors = word.validate()
                if validation_errors:
                    failed_words.append({
                        'word': word.word,
                        'error': f"Validation failed: {', '.join(validation_errors)}"
                    })
                    continue

                # Check for duplicate words (both in existing data and current batch)
                if self.word_exists(word.word) or any(w.word.lower() == word.word.lower() for w in successful_words):
                    duplicate_words.append(word.word)
                    continue

                # Add word to batch
                vocab_data.add_word(word)
                successful_words.append(word)

            except Exception as e:
                failed_words.append({
                    'word': word.word,
                    'error': str(e)
                })

        # Save all successful words at once
        if successful_words:
            self._save_data(vocab_data)

        return {
            'success_count': len(successful_words),
            'error_count': len(failed_words),
            'total_count': len(words),
            'successful_words': successful_words,
            'failed_words': failed_words,
            'duplicate_words': duplicate_words
        }

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
            time_filter: Time filter ('recent_3_days', 'recent_week', 'recent_2_weeks',
                        'recent_month', 'recent_3_months', 'all')

        Returns:
            List of Word instances within the time range
        """
        vocab_data = self._load_data()

        # If 'all' or invalid filter, return all words
        if time_filter == 'all' or time_filter not in TIME_FILTERS:
            filtered_words = vocab_data.vocabulary
        else:
            days = TIME_FILTERS[time_filter]
            cutoff_date = datetime.now() - timedelta(days=days)

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

    def get_time_filter_stats(self) -> Dict[str, int]:
        """
        Get statistics for each time filter category.

        Returns:
            Dictionary with time filter keys and word counts
        """
        vocab_data = self._load_data()
        now = datetime.now()
        stats = {}

        # Calculate count for each time range
        for filter_key, days in TIME_FILTERS.items():
            if days is None:  # 'all' filter
                continue
            cutoff_date = now - timedelta(days=days)
            count = sum(1 for word in vocab_data.vocabulary
                       if word.created_date >= cutoff_date)
            stats[filter_key] = count

        # Add total count
        stats['all'] = len(vocab_data.vocabulary)

        return stats

    def get_words_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Word]:
        """
        Get words within a specific date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of Word instances within the date range
        """
        vocab_data = self._load_data()

        filtered_words = [
            word for word in vocab_data.vocabulary
            if start_date <= word.created_date <= end_date
        ]

        # Sort by creation date (newest first)
        filtered_words.sort(key=lambda w: w.created_date, reverse=True)

        return filtered_words

    def get_learning_progress_stats(self) -> Dict[str, Any]:
        """
        Get detailed learning progress statistics.

        Returns:
            Dictionary with learning progress data
        """
        vocab_data = self._load_data()
        now = datetime.now()

        # Calculate daily stats for the last 30 days
        daily_stats = {}
        for i in range(30):
            date = now - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            count = sum(1 for word in vocab_data.vocabulary
                       if word.created_date.date() == date.date())
            daily_stats[date_str] = count

        # Calculate weekly stats for the last 12 weeks
        weekly_stats = {}
        for i in range(12):
            week_start = now - timedelta(weeks=i+1)
            week_end = now - timedelta(weeks=i)
            week_key = f"Week {i+1}"
            count = sum(1 for word in vocab_data.vocabulary
                       if week_start <= word.created_date <= week_end)
            weekly_stats[week_key] = count

        return {
            'daily_stats': daily_stats,
            'weekly_stats': weekly_stats,
            'total_words': len(vocab_data.vocabulary),
            'average_daily': len(vocab_data.vocabulary) / max(30, 1),
            'most_productive_day': max(daily_stats.items(), key=lambda x: x[1]) if daily_stats else None
        }

    @staticmethod
    def get_time_filter_label(time_filter: str) -> str:
        """
        Get the display label for a time filter.

        Args:
            time_filter: Time filter key

        Returns:
            Display label in Chinese
        """
        return TIME_FILTER_LABELS.get(time_filter, '全部')

    @staticmethod
    def get_all_time_filters() -> Dict[str, str]:
        """
        Get all available time filters with their labels.

        Returns:
            Dictionary mapping filter keys to display labels
        """
        return TIME_FILTER_LABELS.copy()