"""
Unit tests for the vocabulary model classes.
"""

import unittest
from datetime import datetime
from models.vocabulary import Word, VocabularyData


class TestWordModel(unittest.TestCase):
    """Test cases for the Word model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_word_data = {
            "word": "example",
            "chinese_meaning": "例子",
            "english_meaning": "a thing characteristic of its kind",
            "phonetic": "/ɪɡˈzæmpəl/",
            "example_sentence": "This is an example sentence.",
            "synonyms": ["instance", "case", "illustration"],
            "antonyms": ["exception"]
        }

    def test_word_creation_with_required_fields(self):
        """Test creating a word with only required fields."""
        word = Word(
            word="test",
            chinese_meaning="測試"
        )

        self.assertEqual(word.word, "test")
        self.assertEqual(word.chinese_meaning, "測試")
        self.assertEqual(word.english_meaning, "")
        self.assertEqual(word.phonetic, "")
        self.assertEqual(word.example_sentence, "")
        self.assertEqual(word.synonyms, [])
        self.assertEqual(word.antonyms, [])
        self.assertIsNotNone(word.id)
        self.assertIsInstance(word.created_date, datetime)
        self.assertIsInstance(word.updated_date, datetime)

    def test_word_creation_with_all_fields(self):
        """Test creating a word with all fields."""
        word = Word(**self.valid_word_data)

        self.assertEqual(word.word, "example")
        self.assertEqual(word.chinese_meaning, "例子")
        self.assertEqual(word.english_meaning, "a thing characteristic of its kind")
        self.assertEqual(word.phonetic, "/ɪɡˈzæmpəl/")
        self.assertEqual(word.example_sentence, "This is an example sentence.")
        self.assertEqual(word.synonyms, ["instance", "case", "illustration"])
        self.assertEqual(word.antonyms, ["exception"])

    def test_word_creation_with_custom_id(self):
        """Test creating a word with custom ID."""
        custom_id = "custom_word_001"
        word = Word(
            word="test",
            chinese_meaning="測試",
            word_id=custom_id
        )

        self.assertEqual(word.id, custom_id)

    def test_word_validation_success(self):
        """Test successful word validation."""
        word = Word(**self.valid_word_data)
        errors = word.validate()

        self.assertEqual(len(errors), 0)

    def test_word_validation_empty_word(self):
        """Test validation with empty word."""
        word = Word(
            word="",
            chinese_meaning="測試"
        )
        errors = word.validate()

        self.assertIn("英文單字不能為空", errors)

    def test_word_validation_empty_chinese_meaning(self):
        """Test validation with empty Chinese meaning."""
        word = Word(
            word="test",
            chinese_meaning=""
        )
        errors = word.validate()

        self.assertIn("中文解釋不能為空", errors)

    def test_word_validation_word_too_long(self):
        """Test validation with word too long."""
        long_word = "a" * 101
        word = Word(
            word=long_word,
            chinese_meaning="測試"
        )
        errors = word.validate()

        self.assertIn("英文單字長度不能超過100個字符", errors)

    def test_word_validation_chinese_meaning_too_long(self):
        """Test validation with Chinese meaning too long."""
        long_meaning = "測" * 201
        word = Word(
            word="test",
            chinese_meaning=long_meaning
        )
        errors = word.validate()

        self.assertIn("中文解釋長度不能超過200個字符", errors)

    def test_word_validation_multiple_errors(self):
        """Test validation with multiple errors."""
        word = Word(
            word="",
            chinese_meaning=""
        )
        errors = word.validate()

        self.assertEqual(len(errors), 2)
        self.assertIn("英文單字不能為空", errors)
        self.assertIn("中文解釋不能為空", errors)

    def test_word_to_dict(self):
        """Test converting word to dictionary."""
        word = Word(**self.valid_word_data)
        word_dict = word.to_dict()

        self.assertEqual(word_dict["word"], "example")
        self.assertEqual(word_dict["chinese_meaning"], "例子")
        self.assertEqual(word_dict["english_meaning"], "a thing characteristic of its kind")
        self.assertEqual(word_dict["phonetic"], "/ɪɡˈzæmpəl/")
        self.assertEqual(word_dict["example_sentence"], "This is an example sentence.")
        self.assertEqual(word_dict["synonyms"], ["instance", "case", "illustration"])
        self.assertEqual(word_dict["antonyms"], ["exception"])
        self.assertIn("id", word_dict)
        self.assertIn("created_date", word_dict)
        self.assertIn("updated_date", word_dict)

    def test_word_from_dict(self):
        """Test creating word from dictionary."""
        word_dict = {
            "id": "test_id_001",
            "word": "example",
            "chinese_meaning": "例子",
            "english_meaning": "a thing characteristic of its kind",
            "phonetic": "/ɪɡˈzæmpəl/",
            "example_sentence": "This is an example sentence.",
            "synonyms": ["instance", "case", "illustration"],
            "antonyms": ["exception"],
            "created_date": "2025-01-15T10:30:00",
            "updated_date": "2025-01-15T10:30:00"
        }

        word = Word.from_dict(word_dict)

        self.assertEqual(word.id, "test_id_001")
        self.assertEqual(word.word, "example")
        self.assertEqual(word.chinese_meaning, "例子")
        self.assertEqual(word.english_meaning, "a thing characteristic of its kind")
        self.assertEqual(word.phonetic, "/ɪɡˈzæmpəl/")
        self.assertEqual(word.example_sentence, "This is an example sentence.")
        self.assertEqual(word.synonyms, ["instance", "case", "illustration"])
        self.assertEqual(word.antonyms, ["exception"])

    def test_word_from_dict_with_invalid_dates(self):
        """Test creating word from dictionary with invalid dates."""
        word_dict = {
            "word": "test",
            "chinese_meaning": "測試",
            "created_date": "invalid_date",
            "updated_date": "invalid_date"
        }

        word = Word.from_dict(word_dict)

        # Should not raise exception and use current datetime
        self.assertIsInstance(word.created_date, datetime)
        self.assertIsInstance(word.updated_date, datetime)

    def test_word_update_fields(self):
        """Test updating word fields."""
        word = Word(word="test", chinese_meaning="測試")
        original_updated_date = word.updated_date

        # Wait a moment to ensure different timestamp
        import time
        time.sleep(0.01)

        word.update_fields(
            english_meaning="new meaning",
            phonetic="/test/"
        )

        self.assertEqual(word.english_meaning, "new meaning")
        self.assertEqual(word.phonetic, "/test/")
        self.assertGreater(word.updated_date, original_updated_date)

    def test_word_str_representation(self):
        """Test string representation of word."""
        word = Word(word="example", chinese_meaning="例子")

        self.assertEqual(str(word), "example - 例子")

    def test_word_repr_representation(self):
        """Test repr representation of word."""
        word = Word(word="example", chinese_meaning="例子")

        expected = f"Word(id='{word.id}', word='example', chinese_meaning='例子')"
        self.assertEqual(repr(word), expected)

    def test_word_strips_whitespace(self):
        """Test that word strips whitespace from string fields."""
        word = Word(
            word="  example  ",
            chinese_meaning="  例子  ",
            english_meaning="  meaning  ",
            phonetic="  /test/  ",
            example_sentence="  sentence  "
        )

        self.assertEqual(word.word, "example")
        self.assertEqual(word.chinese_meaning, "例子")
        self.assertEqual(word.english_meaning, "meaning")
        self.assertEqual(word.phonetic, "/test/")
        self.assertEqual(word.example_sentence, "sentence")


class TestVocabularyData(unittest.TestCase):
    """Test cases for the VocabularyData model."""

    def setUp(self):
        """Set up test fixtures."""
        self.vocab_data = VocabularyData()
        self.test_word = Word(word="test", chinese_meaning="測試")

    def test_vocabulary_data_initialization(self):
        """Test VocabularyData initialization."""
        vocab_data = VocabularyData()

        self.assertEqual(len(vocab_data.vocabulary), 0)
        self.assertEqual(vocab_data.metadata["total_words"], 0)
        self.assertIn("last_updated", vocab_data.metadata)

    def test_add_word(self):
        """Test adding a word to vocabulary data."""
        self.vocab_data.add_word(self.test_word)

        self.assertEqual(len(self.vocab_data.vocabulary), 1)
        self.assertEqual(self.vocab_data.metadata["total_words"], 1)
        self.assertEqual(self.vocab_data.vocabulary[0], self.test_word)

    def test_remove_word_success(self):
        """Test successfully removing a word."""
        self.vocab_data.add_word(self.test_word)
        result = self.vocab_data.remove_word(self.test_word.id)

        self.assertTrue(result)
        self.assertEqual(len(self.vocab_data.vocabulary), 0)
        self.assertEqual(self.vocab_data.metadata["total_words"], 0)

    def test_remove_word_not_found(self):
        """Test removing a word that doesn't exist."""
        result = self.vocab_data.remove_word("non_existent_id")

        self.assertFalse(result)
        self.assertEqual(len(self.vocab_data.vocabulary), 0)

    def test_find_word_by_id_success(self):
        """Test successfully finding a word by ID."""
        self.vocab_data.add_word(self.test_word)
        found_word = self.vocab_data.find_word_by_id(self.test_word.id)

        self.assertEqual(found_word, self.test_word)

    def test_find_word_by_id_not_found(self):
        """Test finding a word that doesn't exist."""
        found_word = self.vocab_data.find_word_by_id("non_existent_id")

        self.assertIsNone(found_word)

    def test_update_metadata(self):
        """Test updating metadata."""
        original_updated = self.vocab_data.metadata["last_updated"]

        # Wait a moment to ensure different timestamp
        import time
        time.sleep(0.01)

        self.vocab_data.add_word(self.test_word)

        self.assertEqual(self.vocab_data.metadata["total_words"], 1)
        self.assertGreater(self.vocab_data.metadata["last_updated"], original_updated)

    def test_to_dict(self):
        """Test converting vocabulary data to dictionary."""
        self.vocab_data.add_word(self.test_word)
        vocab_dict = self.vocab_data.to_dict()

        self.assertIn("vocabulary", vocab_dict)
        self.assertIn("metadata", vocab_dict)
        self.assertEqual(len(vocab_dict["vocabulary"]), 1)
        self.assertEqual(vocab_dict["metadata"]["total_words"], 1)

    def test_from_dict(self):
        """Test creating vocabulary data from dictionary."""
        vocab_dict = {
            "vocabulary": [
                {
                    "id": "test_id",
                    "word": "example",
                    "chinese_meaning": "例子",
                    "english_meaning": "",
                    "phonetic": "",
                    "example_sentence": "",
                    "synonyms": [],
                    "antonyms": [],
                    "created_date": "2025-01-15T10:30:00",
                    "updated_date": "2025-01-15T10:30:00"
                }
            ],
            "metadata": {
                "total_words": 1,
                "last_updated": "2025-01-15T10:30:00"
            }
        }

        vocab_data = VocabularyData.from_dict(vocab_dict)

        self.assertEqual(len(vocab_data.vocabulary), 1)
        self.assertEqual(vocab_data.vocabulary[0].word, "example")
        self.assertEqual(vocab_data.vocabulary[0].chinese_meaning, "例子")
        self.assertEqual(vocab_data.metadata["total_words"], 1)


if __name__ == '__main__':
    unittest.main()