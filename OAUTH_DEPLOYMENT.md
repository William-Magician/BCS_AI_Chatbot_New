# 🎯 完整部署流程：OAuth 2.0 版本

## ✅ 你的想法已實作！

現在可以將 `token.pickle` 的內容放進 Streamlit Secrets，在雲端自動連線！

## 📊 流程圖

```
本地開發                         Streamlit Cloud 部署
═══════════                      ════════════════════

1. 首次授權                      1. 轉換 token
   ↓                               ↓
python google_drive_utils.py    python token_to_secrets.py
   ↓                               ↓
瀏覽器授權                       生成 .streamlit/secrets.toml
   ↓                               ↓
✅ token.pickle 建立             2. 部署
                                    ↓
2. 執行 App                      推送程式碼到 GitHub
   ↓                               ↓
streamlit run app_emotion...    Streamlit Cloud Settings > Secrets
   ↓                               ↓
✅ 自動使用 token.pickle         貼上 secrets.toml 內容
                                    ↓
                                 ✅ 自動使用 Secrets 中的 token
```

## 🚀 詳細步驟

### 第一步：本地開發與授權

```bash
cd ~/BCS_AI_Chatbot_with_Evaluation_New

# 1. 確認有 credentials.json（從 GCP 下載）
ls credentials.json

# 2. 首次授權（只需要一次）
python google_drive_utils.py
# → 瀏覽器開啟 → 授權 → token.pickle 自動建立

# 3. 測試本地執行
streamlit run app.py
# → ✅ 從 token.pickle 讀取 token
# → 完成對話 → 評分 → 檔案上傳到 Drive
```

### 第二步：準備部署到 Streamlit Cloud

```bash
# 4. 轉換 token 為 secrets 格式
python token_to_secrets.py
# → ✅ 生成 .streamlit/secrets.toml

# 5. 檢視生成的 secrets
cat .streamlit/secrets.toml
```

輸出範例：
```toml
DRIVE_FOLDER_ID = "<your-google-drive-folder-id>"

[oauth_token]
token = "<your-access-token>"
refresh_token = "<your-refresh-token>"
token_uri = "https://oauth2.googleapis.com/token"
client_id = "<your-client-id>.apps.googleusercontent.com"
client_secret = "<your-client-secret>"
scopes = [
  "https://www.googleapis.com/auth/drive.file",
]
```

### 第三步：部署到 Streamlit Cloud

```bash
# 6. 推送程式碼（secrets.toml 不會被上傳，已在 .gitignore）
git add .
git commit -m "Update app"
git push origin main

# 7. 在 Streamlit Cloud 設定 Secrets
```

**Streamlit Cloud 操作**：
1. 開啟你的 app：https://share.streamlit.io/
2. 選擇你的 repository
3. 點擊 **Settings** (⚙️) → **Secrets**
4. 複製 `.streamlit/secrets.toml` 的**完整內容**
5. 貼到 Secrets 編輯器
6. 點擊 **Save**
7. App 會自動重啟

### 第四步：驗證部署

```
Streamlit Cloud Logs 應該顯示：
✅ 從 Streamlit Secrets 讀取 token
✅ Google Drive service 初始化成功
```

測試：
1. 完成一次完整對話
2. 評分
3. 檢查 Google Drive 是否有新檔案上傳

## 🔄 自動偵測邏輯

程式會按照以下優先順序自動選擇：

```python
if HAS_STREAMLIT and 'oauth_token' in st.secrets:
    # 🌐 Streamlit Cloud
    使用 st.secrets['oauth_token']
elif os.path.exists('token.pickle'):
    # 💻 本地開發
    使用 token.pickle
else:
    # 🔐 首次授權
    開啟瀏覽器授權
```

## 📁 檔案說明

| 檔案 | 位置 | 用途 | 上傳到 Git? |
|------|------|------|------------|
| `credentials.json` | 專案根目錄 | OAuth 2.0 憑證 | ❌ 不要 |
| `token.pickle` | 專案根目錄 | 授權 token 快取 | ❌ 不要 |
| `.streamlit/secrets.toml` | 本地測試用 | Secrets 檔案 | ❌ 不要 |
| `.streamlit/secrets.toml.example` | 範本 | Secrets 範例 | ✅ 可以 |
| `token_to_secrets.py` | 轉換工具 | Token → Secrets | ✅ 要 |
| `google_drive_utils.py` | 核心模組 | Drive 整合 | ✅ 要 |

## ⚡ 常見問題

### Q1: Token 會過期嗎？
A: 會，但程式會自動使用 `refresh_token` 更新，你不需要手動處理。

### Q2: 如果 token 失效怎麼辦？
A: 本地重新執行：
```bash
rm token.pickle
python google_drive_utils.py  # 重新授權
python token_to_secrets.py     # 重新轉換
# 更新 Streamlit Cloud Secrets
```

### Q3: secrets.toml 會被上傳到 GitHub 嗎？
A: 不會，已加入 `.gitignore`。這是設計上的安全考量。

### Q4: 能同時有多個使用者嗎？
A: 可以！每個使用者的對話會分別記錄，但都上傳到同一個 Drive 資料夾（使用你的授權）。

### Q5: 本地和 Cloud 能用同一個 token 嗎？
A: 能！就是這個方案的重點。本地用 `token.pickle`，Cloud 用 Secrets，但內容相同。

## 🎉 優勢總結

✅ **保持 OAuth 2.0**：不需要 Service Account  
✅ **個人 Drive**：直接用你的 Google 帳號  
✅ **自動連線**：本地和雲端都不需要瀏覽器授權  
✅ **簡單部署**：只需複製貼上 Secrets  
✅ **自動更新**：Token 過期會自動 refresh  

## 📝 檢查清單

部署前確認：

- [ ] 本地已完成 `python google_drive_utils.py` 授權
- [ ] `token.pickle` 存在
- [ ] 執行 `python token_to_secrets.py` 生成 secrets
- [ ] `.streamlit/secrets.toml` 已建立
- [ ] 本地測試通過（能上傳到 Drive）
- [ ] 程式碼已推送到 GitHub（不包含 secrets.toml）
- [ ] Streamlit Cloud Secrets 已設定
- [ ] 部署後測試通過

---

**現在你的系統已經完全支援 OAuth 2.0 部署了！** 🚀
