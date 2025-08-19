# 🔧 AI API 設定指南

這個模組提供了安全的 API Key 管理功能，支援 OpenAI 和 Google Gemini AI 服務。

## 🚀 快速開始

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 設定 API Keys
```bash
python config/setup_api.py
```

### 3. 檢查設定狀態
```bash
python example_api_setup.py
```

## 📋 功能特色

### 🔐 安全性
- **加密儲存**: 所有 API Keys 都使用 Fernet 加密儲存
- **隱藏檔案**: 加密金鑰儲存在隱藏檔案中
- **不明文儲存**: 設定檔中不會出現明文 API Keys

### 🤖 支援的 AI 服務
- **OpenAI**: GPT-3.5, GPT-4 等模型
- **Google Gemini**: Gemini Pro, Gemini Pro Vision

### ⚙️ 設定選項
- **預設提供商**: 選擇主要使用的 AI 服務
- **超時設定**: API 請求超時時間 (5-120秒)
- **重試次數**: 失敗時的最大重試次數 (0-10次)
- **模型選擇**: 為每個提供商選擇特定模型

## 🛠️ 使用方法

### 命令列設定工具
```bash
python config/setup_api.py
```

提供互動式介面來：
- 設定 OpenAI API Key
- 設定 Gemini API Key
- 調整一般設定
- 查看目前狀態
- 清除 API Keys

### 程式化使用
```python
from config.api_config import api_config

# 設定 API Keys
api_config.set_openai_api_key("your-openai-key")
api_config.set_gemini_api_key("your-gemini-key")

# 取得 API Keys
openai_key = api_config.get_openai_api_key()
gemini_key = api_config.get_gemini_api_key()

# 檢查狀態
status = api_config.get_status_summary()
available_providers = api_config.get_available_providers()

# 設定選項
api_config.set_default_provider("openai")
api_config.set_timeout(30)
api_config.set_max_retries(3)
```

## 🔑 取得 API Keys

### OpenAI API Key
1. 前往 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登入你的帳號
3. 點擊 "Create new secret key"
4. 複製產生的 API Key (格式: sk-...)

### Google Gemini API Key
1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登入你的 Google 帳號
3. 點擊 "Create API Key"
4. 複製產生的 API Key

## 📁 檔案結構

```
config/
├── __init__.py              # 套件初始化
├── api_config.py           # API 設定管理核心
├── setup_api.py            # 命令列設定工具
├── api_keys.json           # 設定檔 (加密儲存)
└── .encryption_key         # 加密金鑰 (隱藏檔案)

tests/
└── test_api_config.py      # 單元測試

example_api_setup.py        # 使用範例
```

## 🧪 測試

執行單元測試：
```bash
python -m pytest tests/test_api_config.py -v
```

測試涵蓋：
- API Key 加密/解密
- 設定檔持久化
- 驗證邏輯
- 錯誤處理
- 邊界條件

## ⚠️ 注意事項

### 安全性
- **不要**將 API Keys 提交到版本控制系統
- **不要**在程式碼中硬編碼 API Keys
- 定期更換 API Keys
- 限制 API Keys 的使用權限

### 檔案管理
- `config/api_keys.json` - 包含加密的設定資料
- `config/.encryption_key` - 加密金鑰，請勿刪除
- 這兩個檔案都應該加入 `.gitignore`

### API 使用限制
- 注意各 AI 服務的使用限額
- 監控 API 使用量和費用
- 設定合理的超時和重試參數

## 🔧 故障排除

### 常見問題

**Q: API Key 設定後無法使用？**
A: 檢查 API Key 格式是否正確，OpenAI 應以 `sk-` 開頭

**Q: 加密金鑰遺失怎麼辦？**
A: 刪除 `config/api_keys.json` 和 `config/.encryption_key`，重新設定

**Q: 如何備份設定？**
A: 使用 `api_config.export_config(include_keys=True)` 匯出設定

**Q: 如何在多個環境間同步設定？**
A: 可以匯出設定後在新環境中重新匯入，但要注意安全性

## 📞 支援

如果遇到問題，請檢查：
1. Python 版本 (建議 3.8+)
2. 依賴套件是否正確安裝
3. API Keys 是否有效
4. 網路連線是否正常

## 🔄 更新日誌

### v1.0.0
- 初始版本
- 支援 OpenAI 和 Gemini API
- 加密儲存功能
- 命令列設定工具
- 完整的單元測試