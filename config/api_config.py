"""
API configuration management for AI services.
"""

import os
import json
from typing import Dict, Optional
from pathlib import Path
from cryptography.fernet import Fernet
import base64


class APIConfigManager:
    """Manages API keys and configuration for AI services."""

    def __init__(self, config_file: str = "config/api_keys.json"):
        """
        Initialize API configuration manager.

        Args:
            config_file: Path to the configuration file
        """
        self.config_file = Path(config_file)
        self.config_dir = self.config_file.parent
        self.config_dir.mkdir(exist_ok=True)

        # Create encryption key file if it doesn't exist
        self.key_file = self.config_dir / ".encryption_key"
        self._ensure_encryption_key()

        # Load existing configuration
        self.config = self._load_config()

    def _ensure_encryption_key(self) -> None:
        """Ensure encryption key exists."""
        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Hide the key file on Windows
            if os.name == 'nt':
                os.system(f'attrib +h "{self.key_file}"')

    def _get_encryption_key(self) -> bytes:
        """Get the encryption key."""
        with open(self.key_file, 'rb') as f:
            return f.read()

    def _encrypt_value(self, value: str) -> str:
        """Encrypt a value."""
        if not value:
            return ""

        key = self._get_encryption_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a value."""
        if not encrypted_value:
            return ""

        try:
            key = self._get_encryption_key()
            fernet = Fernet(key)
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            return ""

    def _load_config(self) -> Dict:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {
                "openai": {
                    "api_key": "",
                    "model": "gpt-5-nano",
                    "enabled": False
                },
                "gemini": {
                    "api_key": "",
                    "model": "gemini-2.5-flash-pro",
                    "enabled": False
                },
                "settings": {
                    "default_provider": "openai",
                    "timeout": 30,
                    "max_retries": 3
                }
            }

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return self._load_config()  # Return default config

    def _save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def set_openai_api_key(self, api_key: str) -> None:
        """
        Set OpenAI API key.

        Args:
            api_key: OpenAI API key
        """
        encrypted_key = self._encrypt_value(api_key)
        self.config["openai"]["api_key"] = encrypted_key
        self.config["openai"]["enabled"] = bool(api_key.strip())
        self._save_config()

    def get_openai_api_key(self) -> str:
        """
        Get OpenAI API key.

        Returns:
            Decrypted OpenAI API key
        """
        encrypted_key = self.config.get("openai", {}).get("api_key", "")
        return self._decrypt_value(encrypted_key)

    def set_gemini_api_key(self, api_key: str) -> None:
        """
        Set Gemini API key.

        Args:
            api_key: Gemini API key
        """
        encrypted_key = self._encrypt_value(api_key)
        self.config["gemini"]["api_key"] = encrypted_key
        self.config["gemini"]["enabled"] = bool(api_key.strip())
        self._save_config()

    def get_gemini_api_key(self) -> str:
        """
        Get Gemini API key.

        Returns:
            Decrypted Gemini API key
        """
        encrypted_key = self.config.get("gemini", {}).get("api_key", "")
        return self._decrypt_value(encrypted_key)

    def is_openai_enabled(self) -> bool:
        """Check if OpenAI is enabled."""
        return self.config.get("openai", {}).get("enabled", False)

    def is_gemini_enabled(self) -> bool:
        """Check if Gemini is enabled."""
        return self.config.get("gemini", {}).get("enabled", False)

    def get_default_provider(self) -> str:
        """Get default AI provider."""
        return self.config.get("settings", {}).get("default_provider", "openai")

    def set_default_provider(self, provider: str) -> None:
        """
        Set default AI provider.

        Args:
            provider: Provider name ("openai" or "gemini")
        """
        if provider in ["openai", "gemini"]:
            self.config["settings"]["default_provider"] = provider
            self._save_config()

    def get_openai_model(self) -> str:
        """Get OpenAI model name."""
        return self.config.get("openai", {}).get("model", "gpt-5-nano")

    def set_openai_model(self, model: str) -> None:
        """
        Set OpenAI model name.

        Args:
            model: Model name
        """
        self.config["openai"]["model"] = model
        self._save_config()

    def get_gemini_model(self) -> str:
        """Get Gemini model name."""
        return self.config.get("gemini", {}).get("model", "gemini-2.5-flash-pro")

    def set_gemini_model(self, model: str) -> None:
        """
        Set Gemini model name.

        Args:
            model: Model name
        """
        self.config["gemini"]["model"] = model
        self._save_config()

    def get_timeout(self) -> int:
        """Get API timeout in seconds."""
        return self.config.get("settings", {}).get("timeout", 30)

    def set_timeout(self, timeout: int) -> None:
        """
        Set API timeout.

        Args:
            timeout: Timeout in seconds
        """
        self.config["settings"]["timeout"] = max(5, min(120, timeout))
        self._save_config()

    def get_max_retries(self) -> int:
        """Get maximum number of retries."""
        return self.config.get("settings", {}).get("max_retries", 3)

    def set_max_retries(self, retries: int) -> None:
        """
        Set maximum number of retries.

        Args:
            retries: Maximum retries
        """
        self.config["settings"]["max_retries"] = max(0, min(10, retries))
        self._save_config()

    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Validate API keys format.

        Returns:
            Dictionary with validation results
        """
        results = {}

        # Validate OpenAI key
        openai_key = self.get_openai_api_key()
        results["openai"] = bool(openai_key and openai_key.startswith("sk-") and len(openai_key) > 20)

        # Validate Gemini key
        gemini_key = self.get_gemini_api_key()
        # Gemini API keys typically start with "AIzaSy" and are 39 characters long
        results["gemini"] = bool(
            gemini_key and
            gemini_key.startswith("AIzaSy") and
            len(gemini_key) == 39 and
            gemini_key.replace("AIzaSy", "").replace("-", "").replace("_", "").isalnum()
        )

        return results

    def get_available_providers(self) -> list:
        """
        Get list of available providers with valid API keys.

        Returns:
            List of available provider names
        """
        available = []
        validation = self.validate_api_keys()

        if validation.get("openai", False):
            available.append("openai")

        if validation.get("gemini", False):
            available.append("gemini")

        return available

    def clear_api_key(self, provider: str) -> None:
        """
        Clear API key for a provider.

        Args:
            provider: Provider name ("openai" or "gemini")
        """
        if provider == "openai":
            self.set_openai_api_key("")
        elif provider == "gemini":
            self.set_gemini_api_key("")

    def export_config(self, include_keys: bool = False) -> Dict:
        """
        Export configuration.

        Args:
            include_keys: Whether to include API keys (decrypted)

        Returns:
            Configuration dictionary
        """
        import copy
        config_copy = copy.deepcopy(self.config)

        if include_keys:
            # Decrypt keys for export
            config_copy["openai"]["api_key"] = self.get_openai_api_key()
            config_copy["gemini"]["api_key"] = self.get_gemini_api_key()
        else:
            # Remove keys from export
            config_copy["openai"]["api_key"] = "***" if self.get_openai_api_key() else ""
            config_copy["gemini"]["api_key"] = "***" if self.get_gemini_api_key() else ""

        return config_copy

    def get_status_summary(self) -> Dict:
        """
        Get status summary of API configuration.

        Returns:
            Status summary dictionary
        """
        validation = self.validate_api_keys()
        available_providers = self.get_available_providers()

        return {
            "openai": {
                "configured": bool(self.get_openai_api_key()),
                "valid": validation.get("openai", False),
                "enabled": self.is_openai_enabled(),
                "model": self.get_openai_model()
            },
            "gemini": {
                "configured": bool(self.get_gemini_api_key()),
                "valid": validation.get("gemini", False),
                "enabled": self.is_gemini_enabled(),
                "model": self.get_gemini_model()
            },
            "settings": {
                "default_provider": self.get_default_provider(),
                "available_providers": available_providers,
                "timeout": self.get_timeout(),
                "max_retries": self.get_max_retries()
            }
        }


# Global instance
api_config = APIConfigManager()