"""
AI service connection testing utilities.
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Tuple
from config.api_config import api_config

# Fix Windows asyncio event loop issue
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class AIServiceTester:
    """Test AI service connections and API keys."""

    @staticmethod
    async def test_openai_connection(api_key: str, model: str = None) -> Tuple[bool, str]:
        """
        Test OpenAI API connection.

        Args:
            api_key: OpenAI API key
            model: Model name to test (optional)

        Returns:
            Tuple of (success, message)
        """
        if not api_key or not api_key.startswith("sk-"):
            return False, "無效的 OpenAI API Key 格式"

        if not model:
            model = api_config.get_openai_model()

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Simple test payload
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "max_tokens": 5,
            "temperature": 0
        }

        try:
            timeout = aiohttp.ClientTimeout(total=api_config.get_timeout())

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:

                    if response.status == 200:
                        return True, f"OpenAI API 連線成功 (模型: {model})"

                    elif response.status == 401:
                        return False, "API Key 無效或已過期"

                    elif response.status == 429:
                        return False, "API 使用量超過限制"

                    elif response.status == 404:
                        return False, f"模型 '{model}' 不存在或無權限使用"

                    else:
                        error_text = await response.text()
                        return False, f"API 錯誤 ({response.status}): {error_text[:100]}"

        except asyncio.TimeoutError:
            return False, f"連線超時 ({api_config.get_timeout()}秒)"

        except aiohttp.ClientError as e:
            return False, f"網路連線錯誤: {str(e)}"

        except Exception as e:
            return False, f"未知錯誤: {str(e)}"

    @staticmethod
    async def test_gemini_connection(api_key: str, model: str = None) -> Tuple[bool, str]:
        """
        Test Gemini API connection.

        Args:
            api_key: Gemini API key
            model: Model name to test (optional)

        Returns:
            Tuple of (success, message)
        """
        if not api_key or not api_key.startswith("AIzaSy"):
            return False, "無效的 Gemini API Key 格式"

        if not model:
            model = api_config.get_gemini_model()

        # Simple test payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "Hello"}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 5,
                "temperature": 0
            }
        }

        try:
            timeout = aiohttp.ClientTimeout(total=api_config.get_timeout())

            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

                async with session.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload
                ) as response:

                    if response.status == 200:
                        return True, f"Gemini API 連線成功 (模型: {model})"

                    elif response.status == 400:
                        error_data = await response.json()
                        error_msg = error_data.get("error", {}).get("message", "請求格式錯誤")
                        return False, f"請求錯誤: {error_msg}"

                    elif response.status == 403:
                        return False, "API Key 無效或無權限"

                    elif response.status == 404:
                        return False, f"模型 '{model}' 不存在"

                    elif response.status == 429:
                        return False, "API 使用量超過限制"

                    else:
                        error_text = await response.text()
                        return False, f"API 錯誤 ({response.status}): {error_text[:100]}"

        except asyncio.TimeoutError:
            return False, f"連線超時 ({api_config.get_timeout()}秒)"

        except aiohttp.ClientError as e:
            return False, f"網路連線錯誤: {str(e)}"

        except Exception as e:
            return False, f"未知錯誤: {str(e)}"

    @staticmethod
    def test_connection_sync(provider: str) -> Tuple[bool, str]:
        """
        Synchronous wrapper for connection testing.

        Args:
            provider: Provider name ("openai" or "gemini")

        Returns:
            Tuple of (success, message)
        """
        try:
            if provider == "openai":
                api_key = api_config.get_openai_api_key()
                if not api_key:
                    return False, "未設定 OpenAI API Key"

                return asyncio.run(AIServiceTester.test_openai_connection(api_key))

            elif provider == "gemini":
                api_key = api_config.get_gemini_api_key()
                if not api_key:
                    return False, "未設定 Gemini API Key"

                return asyncio.run(AIServiceTester.test_gemini_connection(api_key))

            else:
                return False, f"不支援的提供商: {provider}"

        except Exception as e:
            return False, f"測試過程發生錯誤: {str(e)}"

    @staticmethod
    def validate_and_test_key(provider: str, api_key: str) -> Tuple[bool, str]:
        """
        Validate API key format and optionally test connection.

        Args:
            provider: Provider name ("openai" or "gemini")
            api_key: API key to validate

        Returns:
            Tuple of (success, message)
        """
        if provider == "openai":
            if not api_key or not api_key.startswith("sk-") or len(api_key) < 20:
                return False, "OpenAI API Key 格式不正確 (應以 'sk-' 開頭且長度足夠)"

            # Additional format validation
            if len(api_key) < 51:  # OpenAI keys are typically 51 characters
                return False, "OpenAI API Key 長度不足"

            return True, "OpenAI API Key 格式正確"

        elif provider == "gemini":
            if not api_key or not api_key.startswith("AIzaSy"):
                return False, "Gemini API Key 格式不正確 (應以 'AIzaSy' 開頭)"

            if len(api_key) != 39:
                return False, f"Gemini API Key 長度不正確 (應為39字符，目前為{len(api_key)}字符)"

            # Check if the key contains only valid characters
            if not api_key.replace("AIzaSy", "").replace("-", "").replace("_", "").isalnum():
                return False, "Gemini API Key 包含無效字符"

            return True, "Gemini API Key 格式正確"

        else:
            return False, f"不支援的提供商: {provider}"


# Convenience functions
def test_openai_key(api_key: str = None) -> Tuple[bool, str]:
    """Test OpenAI API key."""
    if not api_key:
        api_key = api_config.get_openai_api_key()

    # First validate format
    format_valid, format_msg = AIServiceTester.validate_and_test_key("openai", api_key)
    if not format_valid:
        return format_valid, format_msg

    # Then test connection
    return asyncio.run(AIServiceTester.test_openai_connection(api_key))


def test_gemini_key(api_key: str = None) -> Tuple[bool, str]:
    """Test Gemini API key."""
    if not api_key:
        api_key = api_config.get_gemini_api_key()

    # First validate format
    format_valid, format_msg = AIServiceTester.validate_and_test_key("gemini", api_key)
    if not format_valid:
        return format_valid, format_msg

    # Then test connection
    return asyncio.run(AIServiceTester.test_gemini_connection(api_key))


def validate_key_format(provider: str, api_key: str) -> Tuple[bool, str]:
    """Validate API key format only."""
    return AIServiceTester.validate_and_test_key(provider, api_key)