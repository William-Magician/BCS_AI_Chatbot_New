# BCS AI Chatbot (Evaluation New)

OSCE 醫病溝通模擬系統（Streamlit 版本）。

## 啟動方式

1. 安裝依賴：
	- `pip install -r requirements.txt`
2. 啟動應用：
	- `streamlit run app.py`
	ffmpeg 安裝（非常重要）

本專案的自家 ASR 語音輸入模式會先將錄音檔轉成：

16kHz
mono
pcm_s16le wav

因此 必須安裝 ffmpeg。

Windows

請安裝完整 ffmpeg，並確認可以取得 ffmpeg.exe。

如果系統 PATH 沒有設定好，也可以用環境變數指定：
$env:FFMPEG_PATH="C:\path\to\ffmpeg.exe"
streamlit run app.py
sudo apt update
sudo apt install -y ffmpeg
ffmpeg -version
which ffmpeg
## 部署（Streamlit Cloud）

## 專案重點

- 教案模擬（鼻咽癌、腹痛家屬溝通）
- 對話評分與回饋
- 可選語音互動模式
- Google Drive 對話紀錄上傳（透過 OAuth）
