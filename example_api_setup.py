"""
Example usage of API configuration management.
"""

from config.api_config import api_config


def main():
    """Example of using API configuration."""
    print("🔧 API 設定範例")
    print("=" * 30)

    # Show current status
    print("\n📊 目前狀態:")
    status = api_config.get_status_summary()

    for provider in ["openai", "gemini"]:
        provider_status = status[provider]
        print(f"\n{provider.upper()}:")
        print(f"  已設定: {'✅' if provider_status['configured'] else '❌'}")
        print(f"  有效: {'✅' if provider_status['valid'] else '❌'}")
        print(f"  啟用: {'✅' if provider_status['enabled'] else '❌'}")
        print(f"  模型: {provider_status['model']}")

    # Show available providers
    available = api_config.get_available_providers()
    print(f"\n🚀 可用的 AI 提供商: {', '.join(available) if available else '無'}")

    if available:
        print(f"📌 預設提供商: {api_config.get_default_provider()}")
        print(f"⏱️  超時時間: {api_config.get_timeout()} 秒")
        print(f"🔄 最大重試: {api_config.get_max_retries()} 次")
    else:
        print("\n⚠️  尚未設定任何 API Key")
        print("請執行以下命令來設定:")
        print("python config/setup_api.py")

    # Example of programmatic configuration (commented out for safety)
    """
    # 程式化設定範例 (請小心使用真實的 API Key)

    # 設定 OpenAI
    api_config.set_openai_api_key("your-openai-api-key-here")
    api_config.set_openai_model("gpt-3.5-turbo")

    # 設定 Gemini
    api_config.set_gemini_api_key("your-gemini-api-key-here")
    api_config.set_gemini_model("gemini-pro")

    # 設定預設提供商
    api_config.set_default_provider("openai")

    # 設定超時和重試
    api_config.set_timeout(30)
    api_config.set_max_retries(3)
    """


if __name__ == "__main__":
    main()