import os
import numpy as np
import tensorflow as tf
import librosa

# 這兩行路徑會根據模組相對位置自動找模型與標籤
model_path = os.path.join(os.path.dirname(__file__), 'classifier', 'cnn_model.h5')
labels_path = os.path.join(os.path.dirname(__file__), 'classifier', 'labels.txt')

# 載入指令標籤列表
with open(labels_path, "r", encoding="utf-8") as f:
    COMMANDS = [line.strip() for line in f]

# 載入訓練好的模型
MODEL = tf.keras.models.load_model(model_path, compile=False)

# 引入工具函式
from .utils import fix_mfcc_length

fs = 16000

def predict_command(signal):
    """
    給定一段語音訊號，轉成 MFCC，並利用模型預測指令。
    Args:
        signal (np.ndarray): 音訊資料 (float32)

    Returns:
        tuple(str, float): 預測的指令文字，及信心值(0~1)
    """
    # 計算MFCC特徵
    mfcc = librosa.feature.mfcc(y=signal, sr=fs, n_mfcc=40)
    mfcc = fix_mfcc_length(mfcc, target_frames=32)  # 補齊長度
    mfcc = mfcc[..., np.newaxis]         # 新增 channel 維度 (40,32,1)
    mfcc = np.expand_dims(mfcc, axis=0)  # 新增 batch 維度 (1,40,32,1)

    pred = MODEL.predict(mfcc, verbose=0)[0]  # 模型輸出 (各類別機率)
    idx = int(np.argmax(pred))                # 最大機率索引
    conf = float(pred[idx])                   # 最大機率值 (信心度)
    return COMMANDS[idx], conf
