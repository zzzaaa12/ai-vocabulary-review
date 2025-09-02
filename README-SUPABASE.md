# 英文單字筆記本 - Supabase 版本

這是使用 Vue 3 + Supabase 重新架構的現代化英文單字學習應用程式。

## 🚀 技術棧

- **前端**: Vue 3 + TypeScript + Vite
- **狀態管理**: Pinia
- **路由**: Vue Router 4
- **UI 框架**: Bootstrap 5
- **資料庫**: Supabase (PostgreSQL)
- **認證**: Supabase Auth
- **AI 服務**: Supabase Edge Functions + OpenAI

## 📋 功能特點

### ✨ 核心功能
- 🔐 **現代化認證系統** - Email/密碼登入、Google OAuth
- 📚 **單字管理** - 新增、編輯、刪除、搜尋單字
- 🤖 **AI 自動補齊** - 自動獲取音標、翻譯、例句等
- 📝 **批次新增** - 一次新增多個單字
- 🎯 **智慧複習** - 隨機複習、困難單字標記
- 📊 **學習統計** - 進度追蹤、學習分析

### 🔧 技術特點
- 📱 **響應式設計** - 支援桌面和行動裝置
- ⚡ **即時同步** - 多裝置資料同步
- 🔒 **資料安全** - Row Level Security (RLS)
- 🌐 **PWA 支援** - 可安裝為手機 App
- 🎨 **現代化 UI** - Bootstrap 5 + 自訂樣式

## 🛠️ 開發設定

### 1. 環境需求
- Node.js 18+
- npm 或 yarn
- Supabase 帳號

### 2. 安裝依賴
\`\`\`bash
npm install
\`\`\`

### 3. 環境變數設定
複製 \`.env.example\` 為 \`.env\` 並填入您的 Supabase 設定：

\`\`\`env
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_OPENAI_API_KEY=your_openai_api_key
\`\`\`

### 4. Supabase 設定

#### 4.1 建立資料庫
在 Supabase Dashboard 中執行 \`supabase/migrations/001_initial_schema.sql\`

#### 4.2 部署 Edge Functions
\`\`\`bash
# 安裝 Supabase CLI
npm install -g @supabase/cli

# 登入 Supabase
supabase login

# 部署 Edge Functions
supabase functions deploy ai-generate-word
\`\`\`

#### 4.3 設定環境變數
在 Supabase Dashboard > Settings > Edge Functions 中設定：
- \`OPENAI_API_KEY\`: 您的 OpenAI API 金鑰

### 5. 啟動開發伺服器
\`\`\`bash
npm run dev
\`\`\`

## 📦 部署

### Vercel 部署
1. 將程式碼推送到 GitHub
2. 在 Vercel 中匯入專案
3. 設定環境變數
4. 部署完成

### Netlify 部署
1. 建置專案：\`npm run build\`
2. 上傳 \`dist\` 資料夾到 Netlify
3. 設定環境變數

## 🗄️ 資料庫結構

### users 表
- 使用者基本資訊
- 與 Supabase Auth 整合

### words 表
- 單字資料（單字、翻譯、音標等）
- 支援全文搜尋
- 困難度分級

### review_sessions 表
- 複習記錄
- 學習統計

## 🔐 安全性

- **Row Level Security (RLS)** - 確保使用者只能存取自己的資料
- **API 金鑰保護** - OpenAI API 金鑰在 Edge Functions 中安全存放
- **認證保護** - 所有 API 都需要認證

## 🎯 與原版差異

| 功能 | 原版 (Python/Flask) | 新版 (Vue/Supabase) |
|------|-------------------|---------------------|
| 後端 | Python Flask | Supabase + Edge Functions |
| 資料庫 | JSON 檔案 | PostgreSQL |
| 認證 | 簡單通行碼 | 完整認證系統 |
| 部署 | 需要伺服器 | 靜態網站 + Serverless |
| 擴展性 | 單使用者 | 多使用者 |
| 同步 | 無 | 即時同步 |

## 🚧 開發路線圖

- [ ] 離線支援 (PWA)
- [ ] 語音發音功能
- [ ] 學習提醒通知
- [ ] 匯入/匯出功能
- [ ] 學習統計圖表
- [ ] 社群分享功能

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License