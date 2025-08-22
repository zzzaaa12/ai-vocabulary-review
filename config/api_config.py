"""
API configuration management for AI services.
"""

import os
import json
from typing import Dict, Optional, Tuple
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
                },
                "auth": {
                    "passcode": "",
                    "enabled": False,
                    "auto_logout_enabled": True,
                    "auto_logout_hours": 24,
                    "max_failed_attempts": 5
                },
                "server": {
                    "https_enabled": True,
                    "host": "0.0.0.0",
                    "port": 8080,
                    "cert_file": "certs/cert.pem",
                    "key_file": "certs/key.pem",
                    "force_https": False
                }
            }

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Add server config if it doesn't exist (for backwards compatibility)
                if "server" not in config:
                    config["server"] = {
                        "https_enabled": True,
                        "host": "0.0.0.0",
                        "port": 8080,
                        "cert_file": "certs/cert.pem",
                        "key_file": "certs/key.pem",
                        "force_https": False
                    }
                return config
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

    def set_passcode(self, passcode: str) -> None:
        """
        Set authentication passcode.

        Args:
            passcode: Passcode for website access
        """
        encrypted_passcode = self._encrypt_value(passcode)
        self.config["auth"]["passcode"] = encrypted_passcode
        self.config["auth"]["enabled"] = bool(passcode.strip())
        self._save_config()

    def get_passcode(self) -> str:
        """
        Get authentication passcode.

        Returns:
            Decrypted passcode
        """
        encrypted_passcode = self.config.get("auth", {}).get("passcode", "")
        return self._decrypt_value(encrypted_passcode)

    def is_passcode_configured(self) -> bool:
        """Check if passcode is configured."""
        return bool(self.get_passcode())

    def is_auth_enabled(self) -> bool:
        """Check if authentication is enabled."""
        return self.config.get("auth", {}).get("enabled", False)

    def verify_passcode(self, input_passcode: str) -> bool:
        """
        Verify if the input passcode matches the stored one.

        Args:
            input_passcode: Passcode to verify

        Returns:
            True if passcode matches, False otherwise
        """
        if not self.is_passcode_configured():
            return True  # No passcode configured, allow access

        stored_passcode = self.get_passcode()
        return stored_passcode == input_passcode

    def clear_passcode(self) -> None:
        """Clear the authentication passcode."""
        self.set_passcode("")

    def set_auto_logout_enabled(self, enabled: bool) -> None:
        """
        Set auto logout enabled state.

        Args:
            enabled: Whether auto logout is enabled
        """
        self.config["auth"]["auto_logout_enabled"] = enabled
        self._save_config()

    def is_auto_logout_enabled(self) -> bool:
        """Check if auto logout is enabled."""
        return self.config.get("auth", {}).get("auto_logout_enabled", True)

    def set_auto_logout_hours(self, hours: int) -> None:
        """
        Set auto logout time in hours.

        Args:
            hours: Hours after which user will be auto logged out
        """
        self.config["auth"]["auto_logout_hours"] = max(1, min(168, hours))  # 1 hour to 1 week
        self._save_config()

    def get_auto_logout_hours(self) -> int:
        """Get auto logout hours."""
        return self.config.get("auth", {}).get("auto_logout_hours", 24)

    def set_max_failed_attempts(self, attempts: int) -> None:
        """
        Set maximum failed login attempts.

        Args:
            attempts: Maximum failed attempts before blocking
        """
        self.config["auth"]["max_failed_attempts"] = max(3, min(20, attempts))
        self._save_config()

    def get_max_failed_attempts(self) -> int:
        """Get maximum failed attempts."""
        return self.config.get("auth", {}).get("max_failed_attempts", 5)

    # SSL/HTTPS Configuration Methods

    def set_https_enabled(self, enabled: bool) -> None:
        """
        Set HTTPS enabled state.

        Args:
            enabled: Whether HTTPS is enabled
        """
        if "server" not in self.config:
            self.config["server"] = {}
        self.config["server"]["https_enabled"] = enabled
        self._save_config()

    def is_https_enabled(self) -> bool:
        """Check if HTTPS is enabled."""
        return self.config.get("server", {}).get("https_enabled", True)

    def set_server_host(self, host: str) -> None:
        """
        Set server host.

        Args:
            host: Server host (e.g., '0.0.0.0', '127.0.0.1')
        """
        if "server" not in self.config:
            self.config["server"] = {}
        self.config["server"]["host"] = host
        self._save_config()

    def get_server_host(self) -> str:
        """Get server host."""
        return self.config.get("server", {}).get("host", "0.0.0.0")

    def set_server_port(self, port: int) -> None:
        """
        Set server port.

        Args:
            port: Server port number
        """
        if "server" not in self.config:
            self.config["server"] = {}
        self.config["server"]["port"] = max(1, min(65535, port))
        self._save_config()

    def get_server_port(self) -> int:
        """Get server port."""
        return self.config.get("server", {}).get("port", 8080)

    def set_cert_file(self, cert_file: str) -> None:
        """
        Set SSL certificate file path.

        Args:
            cert_file: Path to SSL certificate file
        """
        if "server" not in self.config:
            self.config["server"] = {}
        self.config["server"]["cert_file"] = cert_file
        self._save_config()

    def get_cert_file(self) -> str:
        """Get SSL certificate file path."""
        return self.config.get("server", {}).get("cert_file", "certs/cert.pem")

    def set_key_file(self, key_file: str) -> None:
        """
        Set SSL private key file path.

        Args:
            key_file: Path to SSL private key file
        """
        if "server" not in self.config:
            self.config["server"] = {}
        self.config["server"]["key_file"] = key_file
        self._save_config()

    def get_key_file(self) -> str:
        """Get SSL private key file path."""
        return self.config.get("server", {}).get("key_file", "certs/key.pem")

    def set_force_https(self, force: bool) -> None:
        """
        Set force HTTPS redirect.

        Args:
            force: Whether to force HTTPS redirect
        """
        if "server" not in self.config:
            self.config["server"] = {}
        self.config["server"]["force_https"] = force
        self._save_config()

    def is_force_https(self) -> bool:
        """Check if force HTTPS redirect is enabled."""
        return self.config.get("server", {}).get("force_https", False)

    def get_ssl_context(self) -> Optional[Tuple[str, str]]:
        """
        Get SSL context for Flask app.

        Returns:
            Tuple of (cert_file, key_file) if both exist, None otherwise
        """
        if not self.is_https_enabled():
            return None

        cert_file = self.get_cert_file()
        key_file = self.get_key_file()

        # Convert relative paths to absolute paths
        if not os.path.isabs(cert_file):
            cert_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), cert_file)
        if not os.path.isabs(key_file):
            key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), key_file)

        if os.path.exists(cert_file) and os.path.exists(key_file):
            return (cert_file, key_file)

        return None

    def validate_ssl_certificates(self) -> Dict[str, bool]:
        """
        Validate SSL certificate files.

        Returns:
            Dictionary with validation results
        """
        cert_file = self.get_cert_file()
        key_file = self.get_key_file()

        # Convert relative paths to absolute paths
        if not os.path.isabs(cert_file):
            cert_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), cert_file)
        if not os.path.isabs(key_file):
            key_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), key_file)

        return {
            "cert_exists": os.path.exists(cert_file),
            "key_exists": os.path.exists(key_file),
            "cert_file": cert_file,
            "key_file": key_file
        }

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
            config_copy["auth"]["passcode"] = self.get_passcode()
        else:
            # Remove keys from export
            config_copy["openai"]["api_key"] = "***" if self.get_openai_api_key() else ""
            config_copy["gemini"]["api_key"] = "***" if self.get_gemini_api_key() else ""
            config_copy["auth"]["passcode"] = "***" if self.get_passcode() else ""

        return config_copy

    def get_status_summary(self) -> Dict:
        """
        Get status summary of API configuration.

        Returns:
            Status summary dictionary
        """
        validation = self.validate_api_keys()
        available_providers = self.get_available_providers()
        ssl_validation = self.validate_ssl_certificates()

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
            },
            "auth": {
                "passcode_configured": self.is_passcode_configured(),
                "auto_logout_enabled": self.is_auto_logout_enabled(),
                "auto_logout_hours": self.get_auto_logout_hours(),
                "max_failed_attempts": self.get_max_failed_attempts()
            },
            "server": {
                "https_enabled": self.is_https_enabled(),
                "host": self.get_server_host(),
                "port": self.get_server_port(),
                "cert_file": self.get_cert_file(),
                "key_file": self.get_key_file(),
                "force_https": self.is_force_https(),
                "ssl_configured": ssl_validation["cert_exists"] and ssl_validation["key_exists"],
                "cert_exists": ssl_validation["cert_exists"],
                "key_exists": ssl_validation["key_exists"]
            }
        }


# Global instance
api_config = APIConfigManager()