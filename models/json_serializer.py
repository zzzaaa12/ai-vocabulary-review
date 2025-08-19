"""
JSON serialization utilities for vocabulary data.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from models.vocabulary import Word, VocabularyData


class VocabularyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for vocabulary data with datetime handling."""

    def default(self, obj):
        """Handle datetime objects and other custom types."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class VocabularyJSONSerializer:
    """JSON serialization and deserialization for vocabulary data."""

    @staticmethod
    def serialize_word(word: Word) -> str:
        """
        Serialize a Word object to JSON string.

        Args:
            word: Word object to serialize

        Returns:
            JSON string representation of the word
        """
        return json.dumps(word.to_dict(), cls=VocabularyJSONEncoder, ensure_ascii=False, indent=2)

    @staticmethod
    def deserialize_word(json_str: str) -> Word:
        """
        Deserialize a JSON string to Word object.

        Args:
            json_str: JSON string containing word data

        Returns:
            Word object

        Raises:
            json.JSONDecodeError: If JSON is invalid
            ValueError: If required fields are missing
        """
        try:
            data = json.loads(json_str)
            return Word.from_dict(data)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON format: {e.msg}", e.doc, e.pos)
        except Exception as e:
            raise ValueError(f"Error creating Word from JSON data: {str(e)}")

    @staticmethod
    def serialize_vocabulary_data(vocab_data: VocabularyData) -> str:
        """
        Serialize VocabularyData object to JSON string.

        Args:
            vocab_data: VocabularyData object to serialize

        Returns:
            JSON string representation of the vocabulary data
        """
        return json.dumps(vocab_data.to_dict(), cls=VocabularyJSONEncoder, ensure_ascii=False, indent=2)

    @staticmethod
    def deserialize_vocabulary_data(json_str: str) -> VocabularyData:
        """
        Deserialize a JSON string to VocabularyData object.

        Args:
            json_str: JSON string containing vocabulary data

        Returns:
            VocabularyData object

        Raises:
            json.JSONDecodeError: If JSON is invalid
            ValueError: If data structure is invalid
        """
        try:
            data = json.loads(json_str)
            return VocabularyData.from_dict(data)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON format: {e.msg}", e.doc, e.pos)
        except Exception as e:
            raise ValueError(f"Error creating VocabularyData from JSON data: {str(e)}")

    @staticmethod
    def serialize_word_list(words: List[Word]) -> str:
        """
        Serialize a list of Word objects to JSON string.

        Args:
            words: List of Word objects to serialize

        Returns:
            JSON string representation of the word list
        """
        word_dicts = [word.to_dict() for word in words]
        return json.dumps(word_dicts, cls=VocabularyJSONEncoder, ensure_ascii=False, indent=2)

    @staticmethod
    def deserialize_word_list(json_str: str) -> List[Word]:
        """
        Deserialize a JSON string to list of Word objects.

        Args:
            json_str: JSON string containing word list data

        Returns:
            List of Word objects

        Raises:
            json.JSONDecodeError: If JSON is invalid
            ValueError: If data structure is invalid
        """
        try:
            data = json.loads(json_str)
            if not isinstance(data, list):
                raise ValueError("JSON data must be a list for word list deserialization")

            words = []
            for word_data in data:
                if not isinstance(word_data, dict):
                    raise ValueError("Each item in the list must be a dictionary")
                words.append(Word.from_dict(word_data))

            return words
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON format: {e.msg}", e.doc, e.pos)
        except Exception as e:
            raise ValueError(f"Error creating word list from JSON data: {str(e)}")

    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """
        Format datetime object to ISO format string.

        Args:
            dt: datetime object to format

        Returns:
            ISO format datetime string
        """
        return dt.isoformat()

    @staticmethod
    def parse_datetime(dt_str: str) -> datetime:
        """
        Parse ISO format datetime string to datetime object.

        Args:
            dt_str: ISO format datetime string

        Returns:
            datetime object

        Raises:
            ValueError: If datetime string is invalid
        """
        try:
            return datetime.fromisoformat(dt_str)
        except ValueError as e:
            raise ValueError(f"Invalid datetime format: {dt_str}. Expected ISO format. Error: {str(e)}")

    @staticmethod
    def validate_json_structure(json_str: str, expected_type: str = "vocabulary") -> bool:
        """
        Validate JSON structure for vocabulary data.

        Args:
            json_str: JSON string to validate
            expected_type: Expected data type ("vocabulary", "word", or "word_list")

        Returns:
            True if structure is valid

        Raises:
            json.JSONDecodeError: If JSON is invalid
            ValueError: If structure is invalid
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON format: {e.msg}", e.doc, e.pos)

        if expected_type == "vocabulary":
            if not isinstance(data, dict):
                raise ValueError("Vocabulary data must be a dictionary")
            if "vocabulary" not in data:
                raise ValueError("Missing 'vocabulary' key in data")
            if not isinstance(data["vocabulary"], list):
                raise ValueError("'vocabulary' must be a list")

        elif expected_type == "word":
            if not isinstance(data, dict):
                raise ValueError("Word data must be a dictionary")
            required_fields = ["word", "chinese_meaning"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

        elif expected_type == "word_list":
            if not isinstance(data, list):
                raise ValueError("Word list data must be a list")
            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    raise ValueError(f"Item {i} in word list must be a dictionary")

        else:
            raise ValueError(f"Unknown expected_type: {expected_type}")

        return True