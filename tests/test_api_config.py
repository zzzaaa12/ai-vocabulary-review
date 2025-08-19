"""
Unit tests for API configuration management.
"""

import unittest
import tempfile
import os
from pathlib import Path
from config.api_config import APIConfigManager


class TestAPIConfigManager(unittest.TestCase):
    """Test cases for APIConfigManager."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test config
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_api_keys.json")
        self.config_manager = APIConfigManager(self.config_file)

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initial_config_creation(self):
        """Test initial configuration creation."""
        # Config should be created with default values
        self.assertFalse(self.config_manager.is_openai_enabled())
        self.assertFalse(self.config_manager.is_gemini_enabled())
        self.assertEqual(self.config_manager.get_default_provider(), "openai")

    def test_openai_api_key_management(self):
        """Test OpenAI API key management."""
        test_key = "sk-test123456789"

        # Set API key
        self.config_manager.set_openai_api_key(test_key)

        # Verify key is stored and encrypted
        retrieved_key = self.config_manager.get_openai_api_key()
        self.assertEqual(retrieved_key, test_key)
        self.assertTrue(self.config_manager.is_openai_enabled())

        # Verify key is encrypted in config file
        raw_config = self.config_manager.config
        stored_key = raw_config["openai"]["api_key"]
        self.assertNotEqual(stored_key, test_key)  # Should be encrypted

    def test_gemini_api_key_management(self):
        """Test Gemini API key management."""
        test_key = "AIzaSyTest123456789"

        # Set API key
        self.config_manager.set_gemini_api_key(test_key)

        # Verify key is stored and encrypted
        retrieved_key = self.config_manager.get_gemini_api_key()
        self.assertEqual(retrieved_key, test_key)
        self.assertTrue(self.config_manager.is_gemini_enabled())

    def test_empty_api_key_handling(self):
        """Test handling of empty API keys."""
        # Set empty key
        self.config_manager.set_openai_api_key("")

        # Should not be enabled
        self.assertFalse(self.config_manager.is_openai_enabled())
        self.assertEqual(self.config_manager.get_openai_api_key(), "")

    def test_model_configuration(self):
        """Test model configuration."""
        # Test OpenAI model
        test_model = "gpt-4"
        self.config_manager.set_openai_model(test_model)
        self.assertEqual(self.config_manager.get_openai_model(), test_model)

        # Test Gemini model
        test_model = "gemini-pro-vision"
        self.config_manager.set_gemini_model(test_model)
        self.assertEqual(self.config_manager.get_gemini_model(), test_model)

    def test_default_provider_setting(self):
        """Test default provider setting."""
        # Test valid provider
        self.config_manager.set_default_provider("gemini")
        self.assertEqual(self.config_manager.get_default_provider(), "gemini")

        # Test invalid provider (should be ignored)
        self.config_manager.set_default_provider("invalid")
        self.assertEqual(self.config_manager.get_default_provider(), "gemini")  # Should remain unchanged

    def test_timeout_and_retries_configuration(self):
        """Test timeout and retries configuration."""
        # Test timeout
        self.config_manager.set_timeout(60)
        self.assertEqual(self.config_manager.get_timeout(), 60)

        # Test timeout bounds
        self.config_manager.set_timeout(200)  # Too high
        self.assertEqual(self.config_manager.get_timeout(), 120)  # Should be capped

        self.config_manager.set_timeout(1)  # Too low
        self.assertEqual(self.config_manager.get_timeout(), 5)  # Should be minimum

        # Test retries
        self.config_manager.set_max_retries(5)
        self.assertEqual(self.config_manager.get_max_retries(), 5)

        # Test retries bounds
        self.config_manager.set_max_retries(20)  # Too high
        self.assertEqual(self.config_manager.get_max_retries(), 10)  # Should be capped

        self.config_manager.set_max_retries(-1)  # Too low
        self.assertEqual(self.config_manager.get_max_retries(), 0)  # Should be minimum

    def test_api_key_validation(self):
        """Test API key validation."""
        # Test valid OpenAI key (51 characters)
        valid_openai_key = "sk-" + "a" * 48
        self.config_manager.set_openai_api_key(valid_openai_key)
        validation = self.config_manager.validate_api_keys()
        self.assertTrue(validation["openai"])

        # Test invalid OpenAI key (wrong prefix)
        self.config_manager.set_openai_api_key("ak-test123456789")
        validation = self.config_manager.validate_api_keys()
        self.assertFalse(validation["openai"])

        # Test invalid OpenAI key (too short)
        self.config_manager.set_openai_api_key("sk-short")
        validation = self.config_manager.validate_api_keys()
        self.assertFalse(validation["openai"])

        # Test valid Gemini key (39 characters)
        valid_gemini_key = "AIzaSy" + "a" * 33
        self.config_manager.set_gemini_api_key(valid_gemini_key)
        validation = self.config_manager.validate_api_keys()
        self.assertTrue(validation["gemini"])

        # Test invalid Gemini key (wrong prefix)
        self.config_manager.set_gemini_api_key("AIzaBy" + "a" * 33)
        validation = self.config_manager.validate_api_keys()
        self.assertFalse(validation["gemini"])

        # Test invalid Gemini key (wrong length)
        self.config_manager.set_gemini_api_key("AIzaSyShort")
        validation = self.config_manager.validate_api_keys()
        self.assertFalse(validation["gemini"])

    def test_available_providers(self):
        """Test getting available providers."""
        # Initially no providers should be available
        providers = self.config_manager.get_available_providers()
        self.assertEqual(len(providers), 0)

        # Add valid OpenAI key
        valid_openai_key = "sk-" + "a" * 48
        self.config_manager.set_openai_api_key(valid_openai_key)
        providers = self.config_manager.get_available_providers()
        self.assertIn("openai", providers)

        # Add valid Gemini key
        valid_gemini_key = "AIzaSy" + "a" * 33
        self.config_manager.set_gemini_api_key(valid_gemini_key)
        providers = self.config_manager.get_available_providers()
        self.assertIn("openai", providers)
        self.assertIn("gemini", providers)

    def test_clear_api_keys(self):
        """Test clearing API keys."""
        # Set keys
        valid_openai_key = "sk-" + "a" * 48
        valid_gemini_key = "AIzaSy" + "a" * 33
        self.config_manager.set_openai_api_key(valid_openai_key)
        self.config_manager.set_gemini_api_key(valid_gemini_key)

        # Verify keys are set
        self.assertTrue(self.config_manager.is_openai_enabled())
        self.assertTrue(self.config_manager.is_gemini_enabled())

        # Clear OpenAI key
        self.config_manager.clear_api_key("openai")
        self.assertFalse(self.config_manager.is_openai_enabled())
        self.assertTrue(self.config_manager.is_gemini_enabled())

        # Clear Gemini key
        self.config_manager.clear_api_key("gemini")
        self.assertFalse(self.config_manager.is_gemini_enabled())

    def test_status_summary(self):
        """Test status summary generation."""
        # Set up configuration
        valid_openai_key = "sk-" + "a" * 48
        valid_gemini_key = "AIzaSy" + "a" * 33
        self.config_manager.set_openai_api_key(valid_openai_key)
        self.config_manager.set_gemini_api_key(valid_gemini_key)

        status = self.config_manager.get_status_summary()

        # Check structure
        self.assertIn("openai", status)
        self.assertIn("gemini", status)
        self.assertIn("settings", status)

        # Check OpenAI status
        self.assertTrue(status["openai"]["configured"])
        self.assertTrue(status["openai"]["valid"])
        self.assertTrue(status["openai"]["enabled"])

        # Check Gemini status
        self.assertTrue(status["gemini"]["configured"])
        self.assertTrue(status["gemini"]["valid"])
        self.assertTrue(status["gemini"]["enabled"])

        # Check settings
        self.assertEqual(len(status["settings"]["available_providers"]), 2)

    def test_export_config(self):
        """Test configuration export."""
        # Set up configuration
        test_openai_key = "sk-" + "a" * 48
        self.config_manager.set_openai_api_key(test_openai_key)

        # Export without keys
        config_without_keys = self.config_manager.export_config(include_keys=False)
        self.assertEqual(config_without_keys["openai"]["api_key"], "***")

        # Export with keys
        config_with_keys = self.config_manager.export_config(include_keys=True)
        self.assertEqual(config_with_keys["openai"]["api_key"], test_openai_key)

    def test_config_persistence(self):
        """Test configuration persistence across instances."""
        # Set configuration in first instance
        test_key = "sk-" + "a" * 48
        self.config_manager.set_openai_api_key(test_key)
        self.config_manager.set_default_provider("openai")

        # Create new instance with same config file
        new_manager = APIConfigManager(self.config_file)

        # Verify configuration is loaded
        self.assertEqual(new_manager.get_openai_api_key(), test_key)
        self.assertEqual(new_manager.get_default_provider(), "openai")
        self.assertTrue(new_manager.is_openai_enabled())


if __name__ == '__main__':
    unittest.main()