# 遷移指南：從 Python/Flask 到 Vue/Supabase

本指南說明如何從原本的 Python Flask 版本遷移到新的 Vue + Supabase 版本。

## 🎯 遷移概述

### 架構變化
```
舊架構: Python Flask + JSON 檔案
新架構: Vue 3 + Supabase + Edge Functions
```

### 主要改進
1. **多使用者支援** - 從單使用者改為多使用者系統
2. **雲端同步** - 資料自動在多裝置間同步
3. **現代化 UI** - 使用 Vue 3 + TypeScript
4. **更好的效能** - 靜態網站 + CDN
5. **更強的安全性** - Row Level Security

## 📋 遷移步驟

### 步驟 1: 資料匯出 (從舊版本)

如果您有現有的單字資料，可以使用以下 Python 腳本匯出：

```python
# export_data.py
import json
from datetime import datetime

def export_vocabulary_data():
    """匯出現有的單字資料"""
    try:
        with open('data/vocabulary.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 轉換格式以符合新的資料庫結構
        exported_words = []
        for word_data in data.get('vocabulary', []):
            exported_word = {
                'word': word_data.get('word', ''),
                'chinese_meaning': word_data.get('chinese_meaning', ''),
                'english_meaning': word_data.get('english_meaning', ''),
                'phonetic': word_data.get('phonetic', ''),
                'example_sentence': word_data.get('example_sentence', ''),
                'synonyms': word_data.get('synonyms', []),
                'antonyms': word_data.get('antonyms', []),
                'created_at': word_data.get('created_date', datetime.now().isoformat())
            }
            exported_words.append(exported_word)
        
        # 儲存匯出檔案
        with open('exported_vocabulary.json', 'w', encoding='utf-8') as f:
            json.dump(exported_words, f, ensure_ascii=False, indent=2)
        
        print(f"成功匯出 {len(exported_words)} 個單字到 exported_vocabulary.json")
        
    except FileNotFoundError:
        print("找不到 vocabulary.json 檔案")
    except Exception as e:
        print(f"匯出失敗: {e}")

if __name__ == "__main__":
    export_vocabulary_data()
```

### 步驟 2: 設定新環境

1. **建立 Supabase 專案**
   - 前往 [Supabase](https://supabase.com)
   - 建立新專案
   - 記錄 Project URL 和 API Key

2. **設定資料庫**
   ```sql
   -- 在 Supabase SQL Editor 中執行
   -- 複製 supabase/migrations/001_initial_schema.sql 的內容
   ```

3. **部署 Edge Functions**
   ```bash
   npm install -g @supabase/cli
   supabase login
   supabase functions deploy ai-generate-word
   ```

### 步驟 3: 資料匯入 (到新版本)

使用新版本的批次新增功能：

1. 登入新系統
2. 前往「批次新增」頁面
3. 將匯出的單字貼上（每行一個單字）
4. 使用 AI 查詢功能重新獲取資料
5. 儲存到新資料庫

或者使用 API 直接匯入：

```javascript
// import_data.js
import { createClient } from '@supabase/supabase-js'
import fs from 'fs'

const supabase = createClient(
  'YOUR_SUPABASE_URL',
  'YOUR_SUPABASE_ANON_KEY'
)

async function importData() {
  // 讀取匯出的資料
  const data = JSON.parse(fs.readFileSync('exported_vocabulary.json', 'utf8'))
  
  // 登入 (需要先註冊帳號)
  const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
    email: 'your-email@example.com',
    password: 'your-password'
  })
  
  if (authError) {
    console.error('登入失敗:', authError)
    return
  }
  
  // 批次插入資料
  const { data: insertData, error: insertError } = await supabase
    .from('words')
    .insert(data.map(word => ({
      ...word,
      user_id: authData.user.id
    })))
  
  if (insertError) {
    console.error('匯入失敗:', insertError)
  } else {
    console.log(`成功匯入 ${data.length} 個單字`)
  }
}

importData()
```

## 🔄 功能對應表

| 舊版功能 | 新版功能 | 說明 |
|---------|---------|------|
| 首頁 | 首頁 | 新增統計資訊和快速操作 |
| 新增單字 | 新增單字 | 介面更現代化 |
| - | 批次新增 | 全新功能 |
| 編輯單字 | 編輯單字 | 功能相同 |
| 隨機複習 | 隨機複習 | 改為批次顯示模式 |
| 搜尋 | 搜尋 | 支援全文搜尋 |
| 通行碼登入 | Email/Google 登入 | 更安全的認證系統 |

## 🚀 部署新版本

### Vercel 部署
1. 將程式碼推送到 GitHub
2. 在 Vercel 匯入專案
3. 設定環境變數
4. 自動部署

### 自訂網域
1. 在 Vercel 設定自訂網域
2. 更新 DNS 設定
3. 啟用 HTTPS

## 🔧 維護和監控

### 資料庫監控
- 使用 Supabase Dashboard 監控資料庫效能
- 設定備份策略

### 錯誤追蹤
- 整合 Sentry 或其他錯誤追蹤服務
- 監控 Edge Functions 執行狀況

### 效能優化
- 使用 Vercel Analytics
- 監控 Core Web Vitals

## 🆘 常見問題

### Q: 如何備份資料？
A: Supabase 提供自動備份，也可以使用 pg_dump 手動備份。

### Q: 如何處理大量資料？
A: 使用分頁查詢和虛擬滾動來處理大量單字。

### Q: 如何自訂 AI 提示？
A: 修改 Edge Function 中的 prompt 內容。

### Q: 如何新增新功能？
A: 使用 Vue 組件系統，遵循現有的程式碼結構。

## 📞 支援

如果在遷移過程中遇到問題，請：
1. 檢查 README-SUPABASE.md
2. 查看 Supabase 文件
3. 提交 GitHub Issue