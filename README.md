# BCS AI Chatbot (Evaluation New)

OSCE 醫病溝通模擬系統（Streamlit 版本）。

## 啟動方式

1. 安裝依賴：
	- `pip install -r requirements.txt`
2. 啟動應用：
	- `streamlit run app.py`

## 部署（Streamlit Cloud）

- 主程式入口：`app.py`
- 機密資訊（OpenAI API Key、OAuth Token）請放在 Streamlit Cloud 的 Secrets。
- 請勿上傳 `credentials.json`、`token.pickle`、`.streamlit/secrets.toml`。

## 專案重點

- 教案模擬（鼻咽癌、腹痛家屬溝通）
- 對話評分與回饋
- 可選語音互動模式
- Google Drive 對話紀錄上傳（透過 OAuth）
