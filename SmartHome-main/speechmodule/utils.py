import os
import librosa
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

fs = 16000  # 取樣率，所有錄音與處理均以16kHz為標準

def record_audio(duration=3, filename='raw_record.wav'):
    """
    使用 sounddevice 錄音指定秒數，存成 WAV 檔。
    Args:
        duration (float): 錄音秒數，預設3秒
        filename (str): 儲存檔名
    
    Returns:
        filename (str): 錄音檔路徑
    """
    print(f"🎙️ 準備錄音，請在 {duration} 秒內說出指令")
    audio = sd.rec(int(fs * duration), samplerate=fs, channels=1, dtype='int16')
    sd.wait()  # 等待錄音結束
    write(filename, fs, audio)  # 寫檔
    print("✅ 錄音完成")
    return filename

def trim_speech(filename, target_duration=1.5):
    """
    使用 librosa 去除錄音檔靜音段，裁剪語音長度。
    Args:
        filename (str): 輸入 WAV 檔
        target_duration (float): 目標音訊長度（秒）

    Returns:
        np.ndarray: 裁剪且補齊後的語音陣列 (float32)
        None: 若未偵測到語音
    """
    y, sr = librosa.load(filename, sr=fs)  # 讀檔並轉成 float32
    intervals = librosa.effects.split(y, top_db=20)  # 靜音區間分割
    if len(intervals) == 0:
        print("⚠️ 沒有偵測到語音，請再試一次")
        return None
    speech = np.concatenate([y[start:end] for start, end in intervals])  # 合併非靜音段
    target_len = int(target_duration * sr)
    # 若不足長度則補零，超過則截斷
    if len(speech) < target_len:
        speech = np.pad(speech, (0, target_len - len(speech)))
    else:
        speech = speech[:target_len]
    return speech

def fix_mfcc_length(mfcc, target_frames=32):
    """
    將 MFCC 時間軸補齊或截斷到目標長度，確保模型輸入尺寸一致。
    Args:
        mfcc (np.ndarray): 輸入 MFCC 特徵 (n_mfcc, 時間軸長)
        target_frames (int): 目標時間軸長度
    
    Returns:
        np.ndarray: 修正後的 MFCC (n_mfcc, target_frames)
    """
    current_frames = mfcc.shape[1]
    if current_frames < target_frames:
        pad_width = target_frames - current_frames
        mfcc = np.pad(mfcc, ((0, 0), (0, pad_width)), mode='constant')
    else:
        mfcc = mfcc[:, :target_frames]
    return mfcc
