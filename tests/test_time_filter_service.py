"""
Unit tests for VocabularyService time filter functionality.
"""

import unittest
import tempfile
import os
from datetime import datetime, timedelta

from services.vocabulary_service import VocabularyService, TIME_FILTERS, TIME_FILTER_LABELS
from models.vocabulary import Word


class TestTimeFilterService(unittest.TestCase):
    """Test cases for time filter functionality in VocabularyService."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()

        self.service = VocabularyService(self.temp_file.name)

        # Create test words with different dates
        now = datetime.now()
        self.test_words = []

        # Create words and manually set their created_date
        word_data = [
            ("recent1", "最近1", "recent word 1", 1),
            ("recent2", "最近2", "recent word 2", 5),
            ("old1", "舊1", "old word 1", 15),
            ("old2", "舊2", "old word 2", 45),
            ("very_old", "很舊", "very old word", 100)
        ]

        for word, chinese, english, days_ago in word_data:
            w = Word(
                word=word,
                chinese_meaning=chinese,
                english_meaning=english
            )
            # Manually set the created_date
            w.created_date = now - timedelta(days=days_ago)
            self.test_words.append(w)

        # Add test words to service
        for word in self.test_words:
            self.service.add_word(word)

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    def test_get_words_by_time_filter_recent_3_days(self):
        """Test filtering words from recent 3 days."""
        words = self.service.get_words_by_time_filter('recent_3_days')

        # Should include words from 1 day ago
        word_names = [w.word for w in words]
        self.assertIn('recent1', word_names)
        self.assertNotIn('recent2', word_names)  # 5 days ago
        self.assertNotIn('old1', word_names)

    def test_get_words_by_time_filter_recent_week(self):
        """Test filtering words from recent week."""
        words = self.service.get_words_by_time_filter('recent_week')

        word_names = [w.word for w in words]
        self.assertIn('recent1', word_names)  # 1 day ago
        self.assertIn('recent2', word_names)  # 5 days ago
        self.assertNotIn('old1', word_names)  # 15 days ago

    def test_get_words_by_time_filter_recent_month(self):
        """Test filtering words from recent month."""
        words = self.service.get_words_by_time_filter('recent_month')

        word_names = [w.word for w in words]
        self.assertIn('recent1', word_names)
        self.assertIn('recent2', word_names)
        self.assertIn('old1', word_names)  # 15 days ago
        self.assertNotIn('old2', word_names)  # 45 days ago

    def test_get_words_by_time_filter_recent_3_months(self):
        """Test filtering words from recent 3 months."""
        words = self.service.get_words_by_time_filter('recent_3_months')

        word_names = [w.word for w in words]
        self.assertIn('recent1', word_names)
        self.assertIn('recent2', word_names)
        self.assertIn('old1', word_names)
        self.assertIn('old2', word_names)  # 45 days ago
        self.assertNotIn('very_old', word_names)  # 100 days ago

    def test_get_words_by_time_filter_all(self):
        """Test getting all words."""
        words = self.service.get_words_by_time_filter('all')

        # Should include all test words
        self.assertEqual(len(words), len(self.test_words))

    def test_get_words_by_time_filter_invalid(self):
        """Test invalid time filter returns all words."""
        words = self.service.get_words_by_time_filter('invalid_filter')

        # Should return all words for invalid filter
        self.assertEqual(len(words), len(self.test_words))

    def test_get_time_filter_stats(self):
        """Test getting time filter statistics."""
        stats = self.service.get_time_filter_stats()

        # Check that all filter keys are present
        expected_keys = ['recent_3_days', 'recent_week', 'recent_2_weeks',
                        'recent_month', 'recent_3_months', 'all']
        for key in expected_keys:
            self.assertIn(key, stats)

        # Check total count
        self.assertEqual(stats['all'], len(self.test_words))

        # Check that recent counts are less than or equal to total
        for key in expected_keys[:-1]:  # Exclude 'all'
            self.assertLessEqual(stats[key], stats['all'])

    def test_get_words_by_date_range(self):
        """Test getting words by specific date range."""
        now = datetime.now()
        start_date = now - timedelta(days=10)
        end_date = now - timedelta(days=2)

        words = self.service.get_words_by_date_range(start_date, end_date)

        # Should include words within the range
        word_names = [w.word for w in words]
        self.assertIn('recent2', word_names)  # 5 days ago
        self.assertNotIn('recent1', word_names)  # 1 day ago (too recent)
        self.assertNotIn('old1', word_names)  # 15 days ago (too old)

    def test_get_learning_progress_stats(self):
        """Test getting learning progress statistics."""
        stats = self.service.get_learning_progress_stats()

        # Check required keys
        required_keys = ['daily_stats', 'weekly_stats', 'total_words',
                        'average_daily', 'most_productive_day']
        for key in required_keys:
            self.assertIn(key, stats)

        # Check data types
        self.assertIsInstance(stats['daily_stats'], dict)
        self.assertIsInstance(stats['weekly_stats'], dict)
        self.assertIsInstance(stats['total_words'], int)
        self.assertIsInstance(stats['average_daily'], float)

        # Check total words count
        self.assertEqual(stats['total_words'], len(self.test_words))

    def test_get_time_filter_label(self):
        """Test getting time filter labels."""
        self.assertEqual(VocabularyService.get_time_filter_label('recent_3_days'), '近三天')
        self.assertEqual(VocabularyService.get_time_filter_label('recent_week'), '近一週')
        self.assertEqual(VocabularyService.get_time_filter_label('all'), '全部')
        self.assertEqual(VocabularyService.get_time_filter_label('invalid'), '全部')

    def test_get_all_time_filters(self):
        """Test getting all time filter options."""
        filters = VocabularyService.get_all_time_filters()

        # Check that all expected filters are present
        expected_filters = ['recent_3_days', 'recent_week', 'recent_2_weeks',
                           'recent_month', 'recent_3_months', 'all']
        for filter_key in expected_filters:
            self.assertIn(filter_key, filters)

        # Check that labels are in Chinese
        self.assertEqual(filters['recent_3_days'], '近三天')
        self.assertEqual(filters['all'], '全部')

    def test_words_sorted_by_date(self):
        """Test that filtered words are sorted by creation date (newest first)."""
        words = self.service.get_words_by_time_filter('all')

        # Check that words are sorted by creation date (newest first)
        for i in range(len(words) - 1):
            self.assertGreaterEqual(words[i].created_date, words[i + 1].created_date)


if __name__ == '__main__':
    unittest.main()