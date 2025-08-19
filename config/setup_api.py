"""
Command-line interface for setting up API keys.
"""

import getpass
from config.api_config import api_config


def setup_openai():
    """Setup OpenAI API configuration."""
    print("\n=== OpenAI 設定 ===")

    current_key = api_config.get_openai_api_key()
    if current_key:
        print(f"目前已設定 OpenAI API Key: {'*' * (len(current_key) - 8) + current_key[-8:]}")
        if input("是否要更新？(y/N): ").lower() != 'y':
            return

    print("請輸入你的 OpenAI API Key (格式: sk-...):")
    print("你可以在 https://platform.openai.com/api-keys 取得")

    api_key = getpass.getpass("OpenAI API Key: ").strip()

    if not api_key:
        print("❌ 未輸入 API Key")
        return

    if not api_key.startswith("sk-"):
        print("⚠️  警告: OpenAI API Key 通常以 'sk-' 開頭")
        if input("確定要繼續？(y/N): ").lower() != 'y':
            return

    # Set API key
    api_config.set_openai_api_key(api_key)

    # Configure model
    print(f"\n目前模型: {api_config.get_openai_model()}")
    print("可用模型: gpt-5-mini, gpt-5-nano (預設), gpt-4.1-mini, gpt-4.1-nano")

    model = input("選擇模型 (直接按 Enter 使用預設): ").strip()
    if model:
        api_config.set_openai_model(model)

    print("✅ OpenAI 設定完成!")


def setup_gemini():
    """Setup Gemini API configuration."""
    print("\n=== Gemini 設定 ===")

    current_key = api_config.get_gemini_api_key()
    if current_key:
        print(f"目前已設定 Gemini API Key: {'*' * (len(current_key) - 8) + current_key[-8:]}")
        if input("是否要更新？(y/N): ").lower() != 'y':
            return

    print("請輸入你的 Gemini API Key:")
    print("你可以在 https://makersuite.google.com/app/apikey 取得")

    api_key = getpass.getpass("Gemini API Key: ").strip()

    if not api_key:
        print("❌ 未輸入 API Key")
        return

    # Set API key
    api_config.set_gemini_api_key(api_key)

    # Configure model
    print(f"\n目前模型: {api_config.get_gemini_model()}")
    print("可用模型: gemini-2.5-flash, gemini-2.5-flash-pro (預設), gemini-2.5-flash-lite")

    model = input("選擇模型 (直接按 Enter 使用預設): ").strip()
    if model:
        api_config.set_gemini_model(model)

    print("✅ Gemini 設定完成!")


def setup_general_settings():
    """Setup general settings."""
    print("\n=== 一般設定 ===")

    # Default provider
    available_providers = api_config.get_available_providers()
    if len(available_providers) > 1:
        print(f"目前預設提供商: {api_config.get_default_provider()}")
        print(f"可用提供商: {', '.join(available_providers)}")

        provider = input("選擇預設提供商 (直接按 Enter 保持不變): ").strip().lower()
        if provider in available_providers:
            api_config.set_default_provider(provider)
            print(f"✅ 預設提供商設定為: {provider}")

    # Timeout
    print(f"\n目前 API 超時時間: {api_config.get_timeout()} 秒")
    timeout_input = input("設定超時時間 (5-120秒，直接按 Enter 保持不變): ").strip()
    if timeout_input.isdigit():
        timeout = int(timeout_input)
        api_config.set_timeout(timeout)
        print(f"✅ 超時時間設定為: {timeout} 秒")

    # Max retries
    print(f"\n目前最大重試次數: {api_config.get_max_retries()}")
    retries_input = input("設定最大重試次數 (0-10次，直接按 Enter 保持不變): ").strip()
    if retries_input.isdigit():
        retries = int(retries_input)
        api_config.set_max_retries(retries)
        print(f"✅ 最大重試次數設定為: {retries}")


def show_status():
    """Show current configuration status."""
    print("\n=== 目前設定狀態 ===")

    status = api_config.get_status_summary()

    # OpenAI status
    openai_status = status["openai"]
    print(f"\n🤖 OpenAI:")
    print(f"   已設定: {'✅' if openai_status['configured'] else '❌'}")
    print(f"   有效: {'✅' if openai_status['valid'] else '❌'}")
    print(f"   啟用: {'✅' if openai_status['enabled'] else '❌'}")
    print(f"   模型: {openai_status['model']}")

    # Gemini status
    gemini_status = status["gemini"]
    print(f"\n🧠 Gemini:")
    print(f"   已設定: {'✅' if gemini_status['configured'] else '❌'}")
    print(f"   有效: {'✅' if gemini_status['valid'] else '❌'}")
    print(f"   啟用: {'✅' if gemini_status['enabled'] else '❌'}")
    print(f"   模型: {gemini_status['model']}")

    # General settings
    settings = status["settings"]
    print(f"\n⚙️  一般設定:")
    print(f"   預設提供商: {settings['default_provider']}")
    print(f"   可用提供商: {', '.join(settings['available_providers']) if settings['available_providers'] else '無'}")
    print(f"   超時時間: {settings['timeout']} 秒")
    print(f"   最大重試: {settings['max_retries']} 次")


def clear_api_keys():
    """Clear API keys."""
    print("\n=== 清除 API Keys ===")

    print("1. 清除 OpenAI API Key")
    print("2. 清除 Gemini API Key")
    print("3. 清除所有 API Keys")
    print("0. 返回")

    choice = input("\n請選擇: ").strip()

    if choice == "1":
        if input("確定要清除 OpenAI API Key？(y/N): ").lower() == 'y':
            api_config.clear_api_key("openai")
            print("✅ OpenAI API Key 已清除")

    elif choice == "2":
        if input("確定要清除 Gemini API Key？(y/N): ").lower() == 'y':
            api_config.clear_api_key("gemini")
            print("✅ Gemini API Key 已清除")

    elif choice == "3":
        if input("確定要清除所有 API Keys？(y/N): ").lower() == 'y':
            api_config.clear_api_key("openai")
            api_config.clear_api_key("gemini")
            print("✅ 所有 API Keys 已清除")


def main():
    """Main setup interface."""
    print("🔧 英文單字筆記本 - AI API 設定工具")
    print("=" * 50)

    while True:
        print("\n請選擇操作:")
        print("1. 設定 OpenAI API")
        print("2. 設定 Gemini API")
        print("3. 一般設定")
        print("4. 查看目前狀態")
        print("5. 清除 API Keys")
        print("0. 退出")

        choice = input("\n請輸入選項 (0-5): ").strip()

        if choice == "1":
            setup_openai()
        elif choice == "2":
            setup_gemini()
        elif choice == "3":
            setup_general_settings()
        elif choice == "4":
            show_status()
        elif choice == "5":
            clear_api_keys()
        elif choice == "0":
            print("\n👋 設定完成，感謝使用!")
            break
        else:
            print("❌ 無效選項，請重新選擇")


if __name__ == "__main__":
    main()