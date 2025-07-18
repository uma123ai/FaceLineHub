import threading
from .utils import record_audio, trim_speech
from .model import predict_command
from scipy.io.wavfile import write
import numpy as np

fs = 16000
trimmed_file = 'trimmed_record.wav'

# 由外部注入的 callback 函式，接收辨識結果，方便 GUI 顯示
result_callback = None

def process():
    """
    錄音→去靜音裁剪→預測指令流程。
    將結果透過 callback 傳出。
    """
    filename = record_audio()
    signal = trim_speech(filename)
    if signal is None:
        if result_callback:
            result_callback("⚠️ 沒有偵測到語音")
        return

    # 儲存裁剪後的音訊檔，方便後續聆聽或調試
    write(trimmed_file, fs, (signal * 32767).astype(np.int16))
    print(f"💾 已儲存裁剪後音訊：{trimmed_file}")

    # 預測並回傳結果
    result, conf = predict_command(signal)
    print(f"🔊 預測結果：{result}（信心值：{conf:.2f}）")
    if result_callback:
        result_callback(f"🔊 指令：{result}\n信心值：{conf:.2f}")

def start_process():
    """
    啟動非同步執行緒執行 process 函式，避免 GUI 卡住。
    """
    threading.Thread(target=process, daemon=True).start()
