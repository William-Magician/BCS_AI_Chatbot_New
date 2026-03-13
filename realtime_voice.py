"""
OpenAI Realtime API 語音對話模組
實現即時語音對話功能
"""

import asyncio
import base64
import json
import os
import threading
import queue
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import websockets
from websockets.sync.client import connect as ws_connect


class RealtimeVoiceSession:
    """
    OpenAI Realtime API 語音會話管理器
    處理即時語音對話的 WebSocket 連接
    """
    
    REALTIME_API_URL = "wss://api.openai.com/v1/realtime"
    MODEL = "gpt-4o-realtime-preview-2024-12-17"
    
    def __init__(
        self,
        api_key: str,
        system_prompt: str = "",
        voice: str = "shimmer",
        on_transcript: Optional[Callable[[str, str], None]] = None,
        on_audio: Optional[Callable[[bytes], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        """
        初始化 Realtime 語音會話
        
        Args:
            api_key: OpenAI API Key
            system_prompt: 系統提示詞
            voice: TTS 語音（alloy, echo, shimmer, ash, ballad, coral, sage, verse）
            on_transcript: 收到逐字稿時的回調函數 (role, text)
            on_audio: 收到音訊時的回調函數 (audio_bytes)
            on_error: 發生錯誤時的回調函數 (error_message)
        """
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.voice = voice
        self.on_transcript = on_transcript
        self.on_audio = on_audio
        self.on_error = on_error
        
        self.ws = None
        self.is_connected = False
        self.is_running = False
        
        # 對話記錄
        self.conversation_history: List[Dict[str, str]] = []
        
        # 音訊隊列
        self.audio_queue = queue.Queue()
        self.response_audio_buffer = bytearray()
        
        # 當前回應的文字
        self.current_response_text = ""
        self.current_user_text = ""
        
    def connect(self) -> bool:
        """建立 WebSocket 連接"""
        try:
            url = f"{self.REALTIME_API_URL}?model={self.MODEL}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1",
            }
            
            self.ws = ws_connect(url, additional_headers=headers)
            self.is_connected = True
            
            # 設定會話配置
            self._configure_session()
            
            return True
            
        except Exception as e:
            if self.on_error:
                self.on_error(f"連接失敗：{str(e)}")
            return False
    
    def _configure_session(self):
        """配置 Realtime 會話"""
        session_config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": self.system_prompt,
                "voice": self.voice,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {
                    "model": "whisper-1"
                },
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.5,
                    "prefix_padding_ms": 300,
                    "silence_duration_ms": 500,
                },
            }
        }
        self._send_event(session_config)
    
    def _send_event(self, event: Dict[str, Any]):
        """發送事件到 WebSocket"""
        if self.ws and self.is_connected:
            try:
                self.ws.send(json.dumps(event))
            except Exception as e:
                if self.on_error:
                    self.on_error(f"發送事件失敗：{str(e)}")
    
    def send_audio(self, audio_bytes: bytes):
        """
        發送音訊數據
        
        Args:
            audio_bytes: PCM16 格式的音訊數據
        """
        if not self.is_connected:
            return
            
        # 將音訊編碼為 base64
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        
        event = {
            "type": "input_audio_buffer.append",
            "audio": audio_b64,
        }
        self._send_event(event)
    
    def commit_audio(self):
        """提交音訊緩衝區（手動模式）"""
        event = {"type": "input_audio_buffer.commit"}
        self._send_event(event)
    
    def send_text(self, text: str):
        """發送文字訊息"""
        if not self.is_connected:
            return
            
        # 創建對話項目
        event = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": text,
                    }
                ]
            }
        }
        self._send_event(event)
        
        # 請求回應
        self._send_event({"type": "response.create"})
        
        # 記錄用戶訊息
        self.conversation_history.append({
            "role": "user",
            "content": text,
            "timestamp": datetime.now().isoformat(),
        })
        
        if self.on_transcript:
            self.on_transcript("user", text)
    
    def receive_events(self) -> bool:
        """
        接收並處理事件（阻塞式）
        
        Returns:
            是否繼續接收
        """
        if not self.ws or not self.is_connected:
            return False
            
        try:
            message = self.ws.recv()
            event = json.loads(message)
            self._handle_event(event)
            return True
            
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False
            return False
        except Exception as e:
            if self.on_error:
                self.on_error(f"接收事件失敗：{str(e)}")
            return False
    
    def _handle_event(self, event: Dict[str, Any]):
        """處理接收到的事件"""
        event_type = event.get("type", "")
        
        if event_type == "session.created":
            # 會話已建立
            pass
            
        elif event_type == "session.updated":
            # 會話配置已更新
            pass
            
        elif event_type == "input_audio_buffer.speech_started":
            # 用戶開始說話
            self.current_user_text = ""
            
        elif event_type == "input_audio_buffer.speech_stopped":
            # 用戶停止說話
            pass
            
        elif event_type == "conversation.item.input_audio_transcription.completed":
            # 用戶語音轉文字完成
            transcript = event.get("transcript", "")
            if transcript:
                self.current_user_text = transcript
                self.conversation_history.append({
                    "role": "user",
                    "content": transcript,
                    "timestamp": datetime.now().isoformat(),
                })
                if self.on_transcript:
                    self.on_transcript("user", transcript)
            
        elif event_type == "response.audio_transcript.delta":
            # AI 回應的文字片段
            delta = event.get("delta", "")
            self.current_response_text += delta
            
        elif event_type == "response.audio_transcript.done":
            # AI 回應的文字完成
            transcript = event.get("transcript", "")
            if transcript:
                self.conversation_history.append({
                    "role": "assistant",
                    "content": transcript,
                    "timestamp": datetime.now().isoformat(),
                })
                if self.on_transcript:
                    self.on_transcript("assistant", transcript)
            self.current_response_text = ""
            
        elif event_type == "response.audio.delta":
            # AI 回應的音訊片段
            audio_b64 = event.get("delta", "")
            if audio_b64:
                audio_bytes = base64.b64decode(audio_b64)
                self.response_audio_buffer.extend(audio_bytes)
                if self.on_audio:
                    self.on_audio(audio_bytes)
                    
        elif event_type == "response.audio.done":
            # AI 回應的音訊完成
            self.response_audio_buffer = bytearray()
            
        elif event_type == "response.done":
            # 完整回應結束
            pass
            
        elif event_type == "error":
            # 錯誤事件
            error_msg = event.get("error", {}).get("message", "未知錯誤")
            if self.on_error:
                self.on_error(error_msg)
    
    def disconnect(self):
        """斷開 WebSocket 連接"""
        self.is_running = False
        self.is_connected = False
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
            self.ws = None
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        獲取對話記錄
        
        Returns:
            對話記錄列表
        """
        return self.conversation_history.copy()
    
    def get_formatted_transcript(self) -> str:
        """
        獲取格式化的逐字稿
        
        Returns:
            格式化的對話逐字稿字串
        """
        lines = []
        for msg in self.conversation_history:
            role = "醫學生" if msg["role"] == "user" else "病人/家屬"
            lines.append(f"{role}：{msg['content']}")
        return "\n".join(lines)


def convert_audio_to_pcm16(audio_bytes: bytes, sample_rate: int = 24000) -> bytes:
    """
    將音訊轉換為 PCM16 格式
    
    Args:
        audio_bytes: 原始音訊數據
        sample_rate: 採樣率（OpenAI Realtime API 需要 24000）
    
    Returns:
        PCM16 格式的音訊數據
    """
    try:
        import io
        import wave
        
        # 嘗試使用 pydub 進行轉換
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            audio = audio.set_frame_rate(sample_rate)
            audio = audio.set_channels(1)
            audio = audio.set_sample_width(2)  # 16-bit
            
            return audio.raw_data
            
        except ImportError:
            # 如果沒有 pydub，假設輸入已經是 PCM16
            return audio_bytes
            
    except Exception as e:
        print(f"音訊轉換失敗：{e}")
        return audio_bytes


def pcm16_to_wav(pcm_data: bytes, sample_rate: int = 24000) -> bytes:
    """
    將 PCM16 數據轉換為 WAV 格式
    
    Args:
        pcm_data: PCM16 音訊數據
        sample_rate: 採樣率
    
    Returns:
        WAV 格式的音訊數據
    """
    import io
    import wave
    
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)
    
    buffer.seek(0)
    return buffer.read()
