# Streamlit Cloud Secrets 設定（安全版）

本文件提供部署時的 Secrets 格式範例，不包含任何真實金鑰。

## Secrets 範例

```toml
OPENAI_API_KEY = "<your-openai-api-key>"
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

## 部署流程

1. 將程式碼推送至 GitHub（不要包含任何 secrets 檔案）
2. 在 Streamlit Cloud 開啟應用設定
3. 進入 Settings → Secrets
4. 貼上上述格式並填入你的真實值
5. 儲存後等待應用自動重啟

## 安全注意事項

- 不要把真實 API Key、Token、Client Secret 寫進 `.md`、`.py`、`.json` 檔案。
- 不要提交 `.streamlit/secrets.toml` 到 Git。
- 若曾外洩金鑰，請立即到對應平台「撤銷並重發」。
