"""
AI-powered word information generation service.
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from config.api_config import api_config

# Fix Windows asyncio event loop issue
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@dataclass
class WordInfo:
    """Data class for AI-generated word information."""
    word: str
    chinese_meaning: str = ""
    english_meaning: str = ""
    phonetic: str = ""
    example_sentence: str = ""
    synonyms: List[str] = None
    antonyms: List[str] = None
    confidence_score: float = 0.0
    provider: str = ""

    def __post_init__(self):
        if self.synonyms is None:
            self.synonyms = []
        if self.antonyms is None:
            self.antonyms = []


class AIWordService:
    """Service for generating word information using AI APIs."""

    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=api_config.get_timeout())
        self.max_retries = api_config.get_max_retries()

    async def generate_word_info(self, word: str, provider: str = None) -> WordInfo:
        """
        Generate comprehensive word information using AI.

        Args:
            word: English word to generate information for
            provider: AI provider to use ("openai" or "gemini"), defaults to configured default

        Returns:
            WordInfo object with generated information

        Raises:
            ValueError: If word is invalid or provider not available
            Exception: If API call fails
        """
        if not word or not word.strip():
            raise ValueError("單字不能為空")

        word = word.strip().lower()

        # Validate word format (basic English word check)
        if not word.replace("-", "").replace("'", "").isalpha():
            raise ValueError("請輸入有效的英文單字")

        # Determine provider
        if not provider:
            provider = api_config.get_default_provider()

        available_providers = api_config.get_available_providers()
        if provider not in available_providers:
            if available_providers:
                provider = available_providers[0]  # Use first available
            else:
                raise ValueError("沒有可用的 AI 提供商，請先設定 API Key")

        # Generate word information
        if provider == "openai":
            return await self._generate_with_openai(word)
        elif provider == "gemini":
            return await self._generate_with_gemini(word)
        else:
            raise ValueError(f"不支援的提供商: {provider}")

    async def _generate_with_openai(self, word: str) -> WordInfo:
        """Generate word information using OpenAI API."""
        api_key = api_config.get_openai_api_key()
        model = api_config.get_openai_model()

        if not api_key:
            raise ValueError("OpenAI API Key 未設定")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Construct prompt for comprehensive word information
        prompt = f"""請為英文單字 "{word}" 提供以下資訊，以JSON格式回應：

{{
    "chinese_meaning": "中文翻譯（簡潔明確）",
    "english_meaning": "英文定義（用英文解釋）",
    "phonetic": "音標（IPA格式，包含斜線）",
    "example_sentence": "例句（展示單字用法）",
    "synonyms": ["同義詞1", "同義詞2", "同義詞3"],
    "antonyms": ["反義詞1", "反義詞2"]
}}

要求：
1. 中文翻譯要準確且常用
2. 英文定義要清楚易懂
3. 音標使用標準IPA格式
4. 例句要自然實用
5. 同義詞和反義詞各提供2-3個
6. 如果是多義詞，提供最常用的意思
7. 只回應JSON，不要其他文字"""

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一個專業的英語詞典助手，專門提供準確的單字資訊。請嚴格按照要求的JSON格式回應。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }

        for attempt in range(self.max_retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=payload
                    ) as response:

                        if response.status == 200:
                            data = await response.json()
                            content = data["choices"][0]["message"]["content"]

                            # Parse JSON response
                            word_data = json.loads(content)

                            # Calculate confidence score based on content quality
                            confidence_score = self._calculate_confidence_score(
                                word_data, word, "openai"
                            )

                            return WordInfo(
                                word=word,
                                chinese_meaning=word_data.get("chinese_meaning", ""),
                                english_meaning=word_data.get("english_meaning", ""),
                                phonetic=word_data.get("phonetic", ""),
                                example_sentence=word_data.get("example_sentence", ""),
                                synonyms=word_data.get("synonyms", []),
                                antonyms=word_data.get("antonyms", []),
                                confidence_score=confidence_score,
                                provider="openai"
                            )

                        elif response.status == 401:
                            raise Exception("OpenAI API Key 無效或已過期")

                        elif response.status == 429:
                            if attempt < self.max_retries:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            raise Exception("OpenAI API 使用量超過限制")

                        elif response.status == 404:
                            raise Exception(f"OpenAI 模型 '{model}' 不存在或無權限使用")

                        else:
                            error_text = await response.text()
                            raise Exception(f"OpenAI API 錯誤 ({response.status}): {error_text[:200]}")

            except json.JSONDecodeError:
                if attempt < self.max_retries:
                    continue
                raise Exception("OpenAI 回應格式錯誤，無法解析JSON")

            except asyncio.TimeoutError:
                if attempt < self.max_retries:
                    continue
                raise Exception(f"OpenAI API 連線超時 ({api_config.get_timeout()}秒)")

            except aiohttp.ClientError as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(1)
                    continue
                raise Exception(f"網路連線錯誤: {str(e)}")

        raise Exception("OpenAI API 呼叫失敗，已達最大重試次數")

    async def _generate_with_gemini(self, word: str) -> WordInfo:
        """Generate word information using Gemini API."""
        api_key = api_config.get_gemini_api_key()
        model = api_config.get_gemini_model()

        if not api_key:
            raise ValueError("Gemini API Key 未設定")

        # Construct prompt for comprehensive word information
        prompt = f"""請為英文單字 "{word}" 提供以下資訊，以JSON格式回應：

{{
    "chinese_meaning": "中文翻譯（簡潔明確）",
    "english_meaning": "英文定義（用英文解釋）",
    "phonetic": "音標（IPA格式，包含斜線）",
    "example_sentence": "例句（展示單字用法）",
    "synonyms": ["同義詞1", "同義詞2", "同義詞3"],
    "antonyms": ["反義詞1", "反義詞2"]
}}

要求：
1. 中文翻譯要準確且常用
2. 英文定義要清楚易懂
3. 音標使用標準IPA格式
4. 例句要自然實用
5. 同義詞和反義詞各提供2-3個
6. 如果是多義詞，提供最常用的意思
7. 只回應JSON，不要其他文字"""

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "maxOutputTokens": 500,
                "temperature": 0.3,
                "responseMimeType": "application/json"
            }
        }

        for attempt in range(self.max_retries + 1):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

                    async with session.post(
                        url,
                        headers={"Content-Type": "application/json"},
                        json=payload
                    ) as response:

                        if response.status == 200:
                            data = await response.json()

                            if "candidates" in data and data["candidates"]:
                                content = data["candidates"][0]["content"]["parts"][0]["text"]

                                # Parse JSON response
                                word_data = json.loads(content)

                                # Calculate confidence score based on content quality
                                confidence_score = self._calculate_confidence_score(
                                    word_data, word, "gemini"
                                )

                                return WordInfo(
                                    word=word,
                                    chinese_meaning=word_data.get("chinese_meaning", ""),
                                    english_meaning=word_data.get("english_meaning", ""),
                                    phonetic=word_data.get("phonetic", ""),
                                    example_sentence=word_data.get("example_sentence", ""),
                                    synonyms=word_data.get("synonyms", []),
                                    antonyms=word_data.get("antonyms", []),
                                    confidence_score=confidence_score,
                                    provider="gemini"
                                )
                            else:
                                raise Exception("Gemini 沒有回應內容")

                        elif response.status == 400:
                            error_data = await response.json()
                            error_msg = error_data.get("error", {}).get("message", "請求格式錯誤")
                            raise Exception(f"Gemini API 請求錯誤: {error_msg}")

                        elif response.status == 403:
                            raise Exception("Gemini API Key 無效或無權限")

                        elif response.status == 404:
                            raise Exception(f"Gemini 模型 '{model}' 不存在")

                        elif response.status == 429:
                            if attempt < self.max_retries:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            raise Exception("Gemini API 使用量超過限制")

                        else:
                            error_text = await response.text()
                            raise Exception(f"Gemini API 錯誤 ({response.status}): {error_text[:200]}")

            except json.JSONDecodeError:
                if attempt < self.max_retries:
                    continue
                raise Exception("Gemini 回應格式錯誤，無法解析JSON")

            except asyncio.TimeoutError:
                if attempt < self.max_retries:
                    continue
                raise Exception(f"Gemini API 連線超時 ({api_config.get_timeout()}秒)")

            except aiohttp.ClientError as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(1)
                    continue
                raise Exception(f"網路連線錯誤: {str(e)}")

        raise Exception("Gemini API 呼叫失敗，已達最大重試次數")

    def _calculate_confidence_score(self, word_data: Dict, original_word: str, provider: str) -> float:
        """
        Calculate confidence score based on AI response quality.

        Args:
            word_data: AI generated word data
            original_word: Original input word
            provider: AI provider used

        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0

        # Base score by provider (40% of total)
        provider_scores = {
            "openai": 0.40,    # OpenAI base reliability
            "gemini": 0.35,    # Gemini base reliability
        }
        score += provider_scores.get(provider, 0.30)

        # Content completeness score (35% of total)
        completeness_score = 0.0
        max_completeness = 0.35

        # Chinese meaning (required - 25% of completeness)
        chinese_meaning = word_data.get("chinese_meaning", "").strip()
        if chinese_meaning:
            if len(chinese_meaning) >= 2 and len(chinese_meaning) <= 20 and not any(char in chinese_meaning for char in ['？', '?', '未知', '不確定']):
                completeness_score += 0.25 * max_completeness
            elif chinese_meaning:
                completeness_score += 0.15 * max_completeness

        # English meaning (20% of completeness)
        english_meaning = word_data.get("english_meaning", "").strip()
        if english_meaning:
            if len(english_meaning) >= 10 and len(english_meaning) <= 100 and not english_meaning.lower().startswith('i don'):
                completeness_score += 0.20 * max_completeness
            elif english_meaning:
                completeness_score += 0.10 * max_completeness

        # Phonetic (15% of completeness)
        phonetic = word_data.get("phonetic", "").strip()
        if phonetic:
            if phonetic.startswith('/') and phonetic.endswith('/') and len(phonetic) > 3:
                completeness_score += 0.15 * max_completeness
            elif phonetic.startswith('[') and phonetic.endswith(']'):
                completeness_score += 0.10 * max_completeness
            elif len(phonetic) > 2:
                completeness_score += 0.05 * max_completeness

        # Example sentence (20% of completeness)
        example = word_data.get("example_sentence", "").strip()
        if example:
            words_in_example = len(example.split())
            if original_word.lower() in example.lower() and words_in_example >= 4 and words_in_example <= 20:
                completeness_score += 0.20 * max_completeness
            elif len(example) >= 10:
                completeness_score += 0.10 * max_completeness

        # Synonyms (10% of completeness)
        synonyms = word_data.get("synonyms", [])
        if isinstance(synonyms, list) and synonyms:
            if len(synonyms) >= 2:
                completeness_score += 0.10 * max_completeness
            else:
                completeness_score += 0.05 * max_completeness

        # Antonyms (10% of completeness)
        antonyms = word_data.get("antonyms", [])
        if isinstance(antonyms, list) and antonyms:
            if len(antonyms) >= 1:
                completeness_score += 0.10 * max_completeness
            else:
                completeness_score += 0.05 * max_completeness

        score += completeness_score

        # Content quality score (25% of total)
        quality_score = 0.0
        max_quality = 0.25

        # Check for error indicators
        error_indicators = ['？', '?', '未知', '不確定', 'unknown', 'not sure', 'unclear']
        has_errors = False

        for field in [chinese_meaning, english_meaning, example]:
            if any(indicator in field.lower() for indicator in error_indicators):
                has_errors = True
                break

        if not has_errors:
            quality_score += 0.40 * max_quality

        # Check phonetic quality
        if phonetic:
            ipa_chars = set('ɪɛæɑɔʊʌəɜɝɚɨɯɤɘɵɞɶœɐɞaeiouɪʏʊɤɯɨəɘɵɞɶœɐɞbpfvθðszʃʒʧʤmnŋlrjwɹɻʔhɦɡkɢqχʁħʕʜʢʡɕʑɺɾɭɳɖɟcɲʎʟɬɮʘǀǃǂǁɓɗʄɠʛ')
            if any(char in ipa_chars for char in phonetic):
                quality_score += 0.30 * max_quality
            elif phonetic.startswith('/') and phonetic.endswith('/'):
                quality_score += 0.20 * max_quality

        # Check example sentence quality
        if example and original_word.lower() in example.lower():
            words_count = len(example.split())
            if 5 <= words_count <= 15:
                quality_score += 0.30 * max_quality
            elif 3 <= words_count <= 20:
                quality_score += 0.20 * max_quality

        score += quality_score

        # Apply penalties for poor quality
        if not chinese_meaning:
            score *= 0.5  # Major penalty for missing Chinese meaning

        if has_errors:
            score *= 0.7  # Penalty for error indicators

        # Ensure score is within valid range
        final_score = max(0.1, min(1.0, score))

        return round(final_score, 3)

    def generate_word_info_sync(self, word: str, provider: str = None) -> WordInfo:
        """
        Synchronous wrapper for generate_word_info.

        Args:
            word: English word to generate information for
            provider: AI provider to use

        Returns:
            WordInfo object with generated information
        """
        return asyncio.run(self.generate_word_info(word, provider))

    async def batch_generate(self, words: List[str], provider: str = None) -> List[WordInfo]:
        """
        Generate information for multiple words concurrently.

        Args:
            words: List of English words
            provider: AI provider to use

        Returns:
            List of WordInfo objects
        """
        if not words:
            return []

        # Limit concurrent requests to avoid rate limiting
        semaphore = asyncio.Semaphore(3)

        async def generate_single(word: str) -> WordInfo:
            async with semaphore:
                try:
                    return await self.generate_word_info(word, provider)
                except Exception as e:
                    # Return error info for failed words
                    return WordInfo(
                        word=word,
                        chinese_meaning=f"生成失敗: {str(e)}",
                        confidence_score=0.0,
                        provider=provider or "unknown"
                    )

        tasks = [generate_single(word) for word in words]
        return await asyncio.gather(*tasks)

    def validate_word(self, word: str) -> Tuple[bool, str]:
        """
        Validate if a word is suitable for AI generation.

        Args:
            word: Word to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not word or not word.strip():
            return False, "單字不能為空"

        word = word.strip()

        if len(word) > 50:
            return False, "單字長度不能超過50個字符"

        if len(word) < 2:
            return False, "單字長度至少需要2個字符"

        # Check for basic English word pattern
        if not word.replace("-", "").replace("'", "").isalpha():
            return False, "請輸入有效的英文單字（只能包含字母、連字號和撇號）"

        # Check for common non-words
        if word.lower() in ["test", "example", "sample", "demo"]:
            return False, "請輸入真實的英文單字"

        return True, ""


# Global service instance
ai_word_service = AIWordService()


# Convenience functions
def generate_word_info(word: str, provider: str = None) -> WordInfo:
    """Generate word information synchronously."""
    return ai_word_service.generate_word_info_sync(word, provider)


def validate_word(word: str) -> Tuple[bool, str]:
    """Validate word for AI generation."""
    return ai_word_service.validate_word(word)


async def generate_word_info_async(word: str, provider: str = None) -> WordInfo:
    """Generate word information asynchronously."""
    return await ai_word_service.generate_word_info(word, provider)