# ai-vocabulary-review

一個以 Flask 打造的英文單字筆記本與隨機複習工具，內建 AI 產生單字資訊（OpenAI/Gemini），支援主題切換、篩選、搜尋與進度統計。

## 特色功能
- 主題系統：橘/藍/綠/灰主題即時切換，整站色彩統一
- AI 快速查詢：輸入單字即自動生成中文、英文定義、音標、例句、同反義詞
- 單字管理：新增、編輯、刪除、搜尋、時間篩選、列表瀏覽
- 隨機複習：卡片式複習介面，支援翻轉、上一個/下一個、鍵盤快捷鍵
- 統計資訊：近三天/一週/一個月等數據與進度條顯示

## Demo 截圖（可選）
- 首頁：AI 快速查詢、單字列表、時間篩選
- 隨機複習：卡片翻轉與控制按鈕（置於頁面內容結尾，footer 上方）

## 安裝需求
- Python 3.8+
- pip

## 快速開始
```bash
# 1) 建立虛擬環境並安裝套件
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2) （可選）設定 AI API（OpenAI / Google Gemini）
python config/setup_api.py

# 3) 啟動開發伺服器
$env:FLASK_APP='app.py'
.\.venv\Scripts\python.exe app.py
# 瀏覽 http://127.0.0.1:8080
```

## 使用說明
- 首頁 `AI 快速查詢`：
  - 輸入英文單字 → 按「AI 查詢」→ 顯示結果於 Modal，可直接儲存為單字
- 單字列表：
  - 右上角提供時間篩選標籤與搜尋列
  - 點選單字可查看詳細資料頁面
- 隨機複習：
  - 導覽列點擊「隨機複習」
  - 以卡片方式瀏覽；空白鍵/Enter 翻面、左右方向鍵切換上一個/下一個

## 設定 AI API（可選）
使用互動式設定工具：
```bash
python config/setup_api.py
```
- 設定 OpenAI/Gemini API Key（安全加密儲存於 `config/api_keys.json`）
- 選擇使用模型、預設提供商、超時時間與重試次數

程式化呼叫：
```python
from config.api_config import api_config
api_config.set_openai_api_key('sk-...')
api_config.set_gemini_api_key('AIzaSy...')
api_config.set_default_provider('openai')
```

## 專案結構
```
mydict_webapp_0820_cursor/
├─ app.py                      # Flask 主要入口與路由
├─ config/
│  ├─ api_config.py           # AI 設定管理與加密
│  └─ setup_api.py            # 互動式設定工具
├─ models/                    # 資料模型（Word 等）
├─ services/                  # 業務邏輯（單字、AI 服務）
├─ templates/                 # Jinja2 模板（含主題化的 UI）
├─ static/
│  └─ css/themes.css          # 主題系統與顏色變數
├─ requirements.txt
└─ LICENSE
```

## 測試
```bash
python -m pytest -q
```

## 部署（簡易）
- 使用反向代理（Nginx）與生產 WSGI（gunicorn/waitress 等）啟動
- 設定環境變數 `SECRET_KEY`，確保 `config/` 下的金鑰與設定檔具備寫入權限

## 授權 License
MIT License，詳見 `LICENSE`。

## 貢獻
歡迎 issue / PR。提交前請：
- 遵守既有程式風格
- 確保單元測試通過


