"""
Unit tests for AI service testing functionality.
"""

import unittest
from unittest.mock import patch, AsyncMock
from services.ai_service_tester import AIServiceTester, validate_key_format


class TestAIServiceTester(unittest.TestCase):
    """Test cases for AIServiceTester."""

    def test_validate_openai_key_format(self):
        """Test OpenAI key format validation."""
        # Valid key
        valid_key = "sk-" + "a" * 48  # 51 characters total
        success, message = validate_key_format("openai", valid_key)
        self.assertTrue(success)
        self.assertIn("格式正確", message)

        # Invalid prefix
        invalid_prefix = "ak-" + "a" * 48
        success, message = validate_key_format("openai", invalid_prefix)
        self.assertFalse(success)
        self.assertIn("sk-", message)

        # Too short
        too_short = "sk-abc"
        success, message = validate_key_format("openai", too_short)
        self.assertFalse(success)
        self.assertIn("長度不足", message)

        # Empty key
        success, message = validate_key_format("openai", "")
        self.assertFalse(success)
        self.assertIn("格式不正確", message)

    def test_validate_gemini_key_format(self):
        """Test Gemini key format validation."""
        # Valid key (39 characters)
        valid_key = "AIzaSy" + "a" * 33  # 39 characters total
        success, message = validate_key_format("gemini", valid_key)
        self.assertTrue(success)
        self.assertIn("格式正確", message)

        # Invalid prefix
        invalid_prefix = "AIzaBy" + "a" * 33
        success, message = validate_key_format("gemini", invalid_prefix)
        self.assertFalse(success)
        self.assertIn("AIzaSy", message)

        # Wrong length
        wrong_length = "AIzaSy" + "a" * 20  # Too short
        success, message = validate_key_format("gemini", wrong_length)
        self.assertFalse(success)
        self.assertIn("長度不正確", message)

        # Invalid characters
        invalid_chars = "AIzaSy" + "!" * 33
        success, message = validate_key_format("gemini", invalid_chars)
        self.assertFalse(success)
        self.assertIn("無效字符", message)

        # Empty key
        success, message = validate_key_format("gemini", "")
        self.assertFalse(success)
        self.assertIn("格式不正確", message)

    def test_validate_invalid_provider(self):
        """Test validation with invalid provider."""
        success, message = validate_key_format("invalid", "test-key")
        self.assertFalse(success)
        self.assertIn("不支援的提供商", message)

    @patch('aiohttp.ClientSession.post')
    async def test_openai_connection_success(self, mock_post):
        """Test successful OpenAI connection."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_post.return_value.__aenter__.return_value = mock_response

        valid_key = "sk-" + "a" * 48
        success, message = await AIServiceTester.test_openai_connection(valid_key, "gpt-5-nano")

        self.assertTrue(success)
        self.assertIn("連線成功", message)
        self.assertIn("gpt-5-nano", message)

    @patch('aiohttp.ClientSession.post')
    async def test_openai_connection_invalid_key(self, mock_post):
        """Test OpenAI connection with invalid key."""
        # Mock 401 response
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_post.return_value.__aenter__.return_value = mock_response

        valid_key = "sk-" + "a" * 48
        success, message = await AIServiceTester.test_openai_connection(valid_key)

        self.assertFalse(success)
        self.assertIn("無效或已過期", message)

    @patch('aiohttp.ClientSession.post')
    async def test_gemini_connection_success(self, mock_post):
        """Test successful Gemini connection."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_post.return_value.__aenter__.return_value = mock_response

        valid_key = "AIzaSy" + "a" * 33
        success, message = await AIServiceTester.test_gemini_connection(valid_key, "gemini-2.5-flash-pro")

        self.assertTrue(success)
        self.assertIn("連線成功", message)
        self.assertIn("gemini-2.5-flash-pro", message)

    @patch('aiohttp.ClientSession.post')
    async def test_gemini_connection_invalid_key(self, mock_post):
        """Test Gemini connection with invalid key."""
        # Mock 403 response
        mock_response = AsyncMock()
        mock_response.status = 403
        mock_post.return_value.__aenter__.return_value = mock_response

        valid_key = "AIzaSy" + "a" * 33
        success, message = await AIServiceTester.test_gemini_connection(valid_key)

        self.assertFalse(success)
        self.assertIn("無效或無權限", message)

    def test_invalid_key_format_openai(self):
        """Test OpenAI connection with invalid key format."""
        import asyncio

        invalid_key = "invalid-key"
        success, message = asyncio.run(AIServiceTester.test_openai_connection(invalid_key))

        self.assertFalse(success)
        self.assertIn("無效的 OpenAI API Key 格式", message)

    def test_invalid_key_format_gemini(self):
        """Test Gemini connection with invalid key format."""
        import asyncio

        invalid_key = "invalid-key"
        success, message = asyncio.run(AIServiceTester.test_gemini_connection(invalid_key))

        self.assertFalse(success)
        self.assertIn("無效的 Gemini API Key 格式", message)


if __name__ == '__main__':
    unittest.main()