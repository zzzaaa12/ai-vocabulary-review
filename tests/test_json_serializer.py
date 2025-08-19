"""
Unit tests for JSON serialization functionality.
"""

import unittest
import json
from datetime import datetime
from models.vocabulary import Word, VocabularyData
from models.json_serializer import VocabularyJSONEncoder, VocabularyJSONSerializer


class TestVocabularyJSONEncoder(unittest.TestCase):
    """Test cases for VocabularyJSONEncoder."""

    def test_datetime_encoding(self):
        """Test encoding datetime objects."""
        dt = datetime(2025, 1, 15, 10, 30, 0)
        encoder = VocabularyJSONEncoder()

        result = encoder.default(dt)

        self.assertEqual(result, "2025-01-15T10:30:00")

    def test_non_datetime_encoding(self):
        """Test encoding non-datetime objects raises TypeError."""
        encoder = VocabularyJSONEncoder()

        with self.assertRaises(TypeError):
            encoder.default(object())


class TestVocabularyJSONSerializer(unittest.TestCase):
    """Test cases for VocabularyJSONSerializer."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_word = Word(
            word="example",
            chinese_meaning="例子",
            english_meaning="a thing characteristic of its kind",
            phonetic="/ɪɡˈzæmpəl/",
            example_sentence="This is an example sentence.",
            synonyms=["instance", "case"],
            antonyms=["exception"]
        )

        self.vocab_data = VocabularyData()
        self.vocab_data.add_word(self.test_word)

    def test_serialize_word(self):
        """Test serializing a Word object."""
        json_str = VocabularyJSONSerializer.serialize_word(self.test_word)

        # Verify it's valid JSON
        data = json.loads(json_str)

        self.assertEqual(data["word"], "example")
        self.assertEqual(data["chinese_meaning"], "例子")
        self.assertEqual(data["english_meaning"], "a thing characteristic of its kind")
        self.assertEqual(data["phonetic"], "/ɪɡˈzæmpəl/")
        self.assertEqual(data["example_sentence"], "This is an example sentence.")
        self.assertEqual(data["synonyms"], ["instance", "case"])
        self.assertEqual(data["antonyms"], ["exception"])
        self.assertIn("id", data)
        self.assertIn("created_date", data)
        self.assertIn("updated_date", data)

    def test_deserialize_word(self):
        """Test deserializing a Word object."""
        json_str = VocabularyJSONSerializer.serialize_word(self.test_word)
        deserialized_word = VocabularyJSONSerializer.deserialize_word(json_str)

        self.assertEqual(deserialized_word.word, self.test_word.word)
        self.assertEqual(deserialized_word.chinese_meaning, self.test_word.chinese_meaning)
        self.assertEqual(deserialized_word.english_meaning, self.test_word.english_meaning)
        self.assertEqual(deserialized_word.phonetic, self.test_word.phonetic)
        self.assertEqual(deserialized_word.example_sentence, self.test_word.example_sentence)
        self.assertEqual(deserialized_word.synonyms, self.test_word.synonyms)
        self.assertEqual(deserialized_word.antonyms, self.test_word.antonyms)

    def test_deserialize_word_invalid_json(self):
        """Test deserializing invalid JSON raises JSONDecodeError."""
        invalid_json = "{ invalid json }"

        with self.assertRaises(json.JSONDecodeError):
            VocabularyJSONSerializer.deserialize_word(invalid_json)

    def test_deserialize_word_missing_fields(self):
        """Test deserializing word with missing required fields."""
        incomplete_json = '{"word": "test"}'  # Missing chinese_meaning

        # Should not raise error as from_dict handles missing fields gracefully
        word = VocabularyJSONSerializer.deserialize_word(incomplete_json)
        self.assertEqual(word.word, "test")
        self.assertEqual(word.chinese_meaning, "")

    def test_serialize_vocabulary_data(self):
        """Test serializing VocabularyData object."""
        json_str = VocabularyJSONSerializer.serialize_vocabulary_data(self.vocab_data)

        # Verify it's valid JSON
        data = json.loads(json_str)

        self.assertIn("vocabulary", data)
        self.assertIn("metadata", data)
        self.assertEqual(len(data["vocabulary"]), 1)
        self.assertEqual(data["vocabulary"][0]["word"], "example")
        self.assertEqual(data["metadata"]["total_words"], 1)

    def test_deserialize_vocabulary_data(self):
        """Test deserializing VocabularyData object."""
        json_str = VocabularyJSONSerializer.serialize_vocabulary_data(self.vocab_data)
        deserialized_data = VocabularyJSONSerializer.deserialize_vocabulary_data(json_str)

        self.assertEqual(len(deserialized_data.vocabulary), 1)
        self.assertEqual(deserialized_data.vocabulary[0].word, "example")
        self.assertEqual(deserialized_data.metadata["total_words"], 1)

    def test_deserialize_vocabulary_data_invalid_json(self):
        """Test deserializing invalid JSON raises JSONDecodeError."""
        invalid_json = "{ invalid json }"

        with self.assertRaises(json.JSONDecodeError):
            VocabularyJSONSerializer.deserialize_vocabulary_data(invalid_json)

    def test_serialize_word_list(self):
        """Test serializing a list of Word objects."""
        word2 = Word(word="test", chinese_meaning="測試")
        words = [self.test_word, word2]

        json_str = VocabularyJSONSerializer.serialize_word_list(words)

        # Verify it's valid JSON
        data = json.loads(json_str)

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["word"], "example")
        self.assertEqual(data[1]["word"], "test")

    def test_deserialize_word_list(self):
        """Test deserializing a list of Word objects."""
        word2 = Word(word="test", chinese_meaning="測試")
        words = [self.test_word, word2]

        json_str = VocabularyJSONSerializer.serialize_word_list(words)
        deserialized_words = VocabularyJSONSerializer.deserialize_word_list(json_str)

        self.assertEqual(len(deserialized_words), 2)
        self.assertEqual(deserialized_words[0].word, "example")
        self.assertEqual(deserialized_words[1].word, "test")

    def test_deserialize_word_list_invalid_json(self):
        """Test deserializing invalid JSON raises JSONDecodeError."""
        invalid_json = "{ invalid json }"

        with self.assertRaises(json.JSONDecodeError):
            VocabularyJSONSerializer.deserialize_word_list(invalid_json)

    def test_deserialize_word_list_not_list(self):
        """Test deserializing non-list data raises ValueError."""
        not_list_json = '{"word": "test"}'

        with self.assertRaises(ValueError) as context:
            VocabularyJSONSerializer.deserialize_word_list(not_list_json)

        self.assertIn("must be a list", str(context.exception))

    def test_deserialize_word_list_invalid_items(self):
        """Test deserializing list with non-dict items raises ValueError."""
        invalid_items_json = '["not_a_dict", "also_not_a_dict"]'

        with self.assertRaises(ValueError) as context:
            VocabularyJSONSerializer.deserialize_word_list(invalid_items_json)

        self.assertIn("must be a dictionary", str(context.exception))

    def test_format_datetime(self):
        """Test formatting datetime to ISO string."""
        dt = datetime(2025, 1, 15, 10, 30, 0)

        result = VocabularyJSONSerializer.format_datetime(dt)

        self.assertEqual(result, "2025-01-15T10:30:00")

    def test_parse_datetime(self):
        """Test parsing ISO datetime string."""
        dt_str = "2025-01-15T10:30:00"

        result = VocabularyJSONSerializer.parse_datetime(dt_str)

        self.assertEqual(result, datetime(2025, 1, 15, 10, 30, 0))

    def test_parse_datetime_invalid(self):
        """Test parsing invalid datetime string raises ValueError."""
        invalid_dt_str = "invalid_datetime"

        with self.assertRaises(ValueError) as context:
            VocabularyJSONSerializer.parse_datetime(invalid_dt_str)

        self.assertIn("Invalid datetime format", str(context.exception))

    def test_validate_json_structure_vocabulary_valid(self):
        """Test validating valid vocabulary JSON structure."""
        json_str = VocabularyJSONSerializer.serialize_vocabulary_data(self.vocab_data)

        result = VocabularyJSONSerializer.validate_json_structure(json_str, "vocabulary")

        self.assertTrue(result)

    def test_validate_json_structure_vocabulary_invalid_not_dict(self):
        """Test validating vocabulary JSON that's not a dictionary."""
        invalid_json = '["not", "a", "dict"]'

        with self.assertRaises(ValueError) as context:
            VocabularyJSONSerializer.validate_json_structure(invalid_json, "vocabulary")

        self.assertIn("must be a dictionary", str(context.exception))

    def test_validate_json_structure_vocabulary_missing_key(self):
        """Test validating vocabulary JSON missing vocabulary key."""
        invalid_json = '{"metadata": {"total_words": 0}}'

        with self.assertRaises(ValueError) as context:
            VocabularyJSONSerializer.validate_json_structure(invalid_json, "vocabulary")

        self.assertIn("Missing 'vocabulary' key", str(context.exception))

    def test_validate_json_structure_vocabulary_invalid_list(self):
        """Test validating vocabulary JSON with non-list vocabulary."""
        invalid_json = '{"vocabulary": "not_a_list"}'

        with self.assertRaises(ValueError) as context:
            VocabularyJSONSerializer.validate_json_structure(invalid_json, "vocabulary")

        self.assertIn("'vocabulary' must be a list", str(context.exception))

    def test_validate_json_structure_word_valid(self):
        """Test validating valid word JSON structure."""
        json_str = VocabularyJSONSerializer.serialize_word(self.test_word)

        result = VocabularyJSONSerializer.validate_json_structure(json_str, "word")

        self.assertTrue(result)

    def test_validate_json_structure_word_not_dict(self):
        """Test validating word JSON that's not a dictionary."""
        invalid_json = '["not", "a", "dict"]'

        with self.assertRaises(ValueError) as context:
            VocabularyJSONSerializer.validate_json_structure(invalid_json, "word")

        self.assertIn("must be a dictionary", str(context.exception))

    def test_validate_json_structure_word_missing_required_field(self):
        """Test validating word JSON missing required fields."""
        invalid_json = '{"word": "test"}'  # Missing chinese_meaning

        with self.assertRaises(ValueError) as context:
            VocabularyJSONSerializer.validate_json_structure(invalid_json, "word")

        self.assertIn("Missing required field: chinese_meaning", str(context.exception))

    def test_validate_json_structure_word_list_valid(self):
        """Test validating valid word list JSON structure."""
        words = [self.test_word]
        json_str = VocabularyJSONSerializer.serialize_word_list(words)

        result = VocabularyJSONSerializer.validate_json_structure(json_str, "word_list")

        self.assertTrue(result)

    def test_validate_json_structure_word_list_not_list(self):
        """Test validating word list JSON that's not a list."""
        invalid_json = '{"not": "a_list"}'

        with self.assertRaises(ValueError) as context:
            VocabularyJSONSerializer.validate_json_structure(invalid_json, "word_list")

        self.assertIn("must be a list", str(context.exception))

    def test_validate_json_structure_word_list_invalid_items(self):
        """Test validating word list JSON with non-dict items."""
        invalid_json = '["not_a_dict"]'

        with self.assertRaises(ValueError) as context:
            VocabularyJSONSerializer.validate_json_structure(invalid_json, "word_list")

        self.assertIn("must be a dictionary", str(context.exception))

    def test_validate_json_structure_invalid_json(self):
        """Test validating invalid JSON raises JSONDecodeError."""
        invalid_json = "{ invalid json }"

        with self.assertRaises(json.JSONDecodeError):
            VocabularyJSONSerializer.validate_json_structure(invalid_json, "vocabulary")

    def test_validate_json_structure_unknown_type(self):
        """Test validating with unknown expected type raises ValueError."""
        json_str = '{"test": "data"}'

        with self.assertRaises(ValueError) as context:
            VocabularyJSONSerializer.validate_json_structure(json_str, "unknown_type")

        self.assertIn("Unknown expected_type", str(context.exception))

    def test_chinese_characters_preservation(self):
        """Test that Chinese characters are properly preserved in serialization."""
        word_with_chinese = Word(
            word="測試",
            chinese_meaning="這是一個測試單字",
            english_meaning="This is a test word"
        )

        json_str = VocabularyJSONSerializer.serialize_word(word_with_chinese)
        deserialized_word = VocabularyJSONSerializer.deserialize_word(json_str)

        self.assertEqual(deserialized_word.word, "測試")
        self.assertEqual(deserialized_word.chinese_meaning, "這是一個測試單字")

        # Verify Chinese characters are readable in JSON
        self.assertIn("測試", json_str)
        self.assertIn("這是一個測試單字", json_str)

    def test_round_trip_serialization(self):
        """Test complete round-trip serialization maintains data integrity."""
        # Create complex vocabulary data
        word1 = Word(
            word="complex",
            chinese_meaning="複雜的",
            english_meaning="consisting of many interconnected parts",
            phonetic="/ˈkɒmpleks/",
            example_sentence="This is a complex problem.",
            synonyms=["complicated", "intricate"],
            antonyms=["simple", "easy"]
        )

        word2 = Word(
            word="simple",
            chinese_meaning="簡單的",
            english_meaning="easily understood or done",
            phonetic="/ˈsɪmpəl/",
            example_sentence="This is a simple task.",
            synonyms=["easy", "basic"],
            antonyms=["complex", "difficult"]
        )

        vocab_data = VocabularyData()
        vocab_data.add_word(word1)
        vocab_data.add_word(word2)

        # Serialize and deserialize
        json_str = VocabularyJSONSerializer.serialize_vocabulary_data(vocab_data)
        deserialized_data = VocabularyJSONSerializer.deserialize_vocabulary_data(json_str)

        # Verify all data is preserved
        self.assertEqual(len(deserialized_data.vocabulary), 2)

        # Check first word
        word1_deserialized = deserialized_data.vocabulary[0]
        self.assertEqual(word1_deserialized.word, "complex")
        self.assertEqual(word1_deserialized.chinese_meaning, "複雜的")
        self.assertEqual(word1_deserialized.synonyms, ["complicated", "intricate"])
        self.assertEqual(word1_deserialized.antonyms, ["simple", "easy"])

        # Check second word
        word2_deserialized = deserialized_data.vocabulary[1]
        self.assertEqual(word2_deserialized.word, "simple")
        self.assertEqual(word2_deserialized.chinese_meaning, "簡單的")
        self.assertEqual(word2_deserialized.synonyms, ["easy", "basic"])
        self.assertEqual(word2_deserialized.antonyms, ["complex", "difficult"])

        # Check metadata
        self.assertEqual(deserialized_data.metadata["total_words"], 2)


if __name__ == '__main__':
    unittest.main()