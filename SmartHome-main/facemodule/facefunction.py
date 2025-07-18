import os
import cv2
import face_recognition
import numpy as np
import time
import datetime
import pandas as pd

def save_log(name, result, excel_path="log.xlsx"):
    """
    儲存辨識結果到 Excel 檔中，包含時間、人名與結果。
    Save face recognition result to an Excel log file.

    Args:
        name (str): 被辨識者名字或 Unknown。
        result (str): 辨識結果，例如 "Success" 或 "Unknown"。
        excel_path (str): log 儲存位置，預設為 'log.xlsx'。
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {"Time": now, "Name": name, "Result": result}

    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path, engine="openpyxl")
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_excel(excel_path, index=False, engine="openpyxl")
    print(f"📄 Log saved: {row}")

def save_unknown_image(frame, folder="unknown_faces"):
    """
    若辨識為 Unknown，將該 frame 存圖以供後續比對或新增白名單。
    Save image of unrecognized face (unknown) to specified folder.

    Args:
        frame (np.ndarray): OpenCV 影像。
        folder (str): 儲存資料夾名稱。
    """
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(folder, f"unknown_{timestamp}.jpg")
    success = cv2.imwrite(path, frame)
    if success:
        print(f"📸 Unknown face saved to: {path}")
    else:
        print(f"⚠️ Failed to save image to: {path}")

def load_facedata(folder="facemodule/facedata"):
    """
    載入事先儲存的人臉特徵向量（.npy 檔案）。
    Load known face vectors and names from .npy files.

    Returns:
        known_encodings (List[np.ndarray]): 臉部特徵向量。
        known_names (List[str]): 對應的人名。
    """
    os.makedirs(folder, exist_ok=True)
    known_encodings = []
    known_names = []

    print(f"📁 嘗試載入資料夾: {folder}")
    for file in os.listdir(folder):
        if file.endswith(".npy"):
            path = os.path.join(folder, file)
            name = os.path.splitext(file)[0]
            try:
                vector = np.load(path)
                print(f"✅ {file} 載入成功！Shape: {vector.shape}, 前5項: {vector[:5]}")
                known_encodings.append(vector)
                known_names.append(name)
            except Exception as e:
                print(f"❌ {file} 載入失敗！錯誤: {e}")

    print(f"🔍 共載入 {len(known_encodings)} 個向量。")
    return known_encodings, known_names

def process_frame(frame, known_encodings, known_names, state):
    """
    分析單張影像：偵測人臉、比對向量、回傳辨識後畫面與名字。

    Args:
        frame (np.ndarray): OpenCV 擷取影像。
        known_encodings (List[np.ndarray]): 白名單向量。
        known_names (List[str]): 白名單名字。
        state (dict): 保持歷史狀態，包含 last_name、elapsed 時間等。

    Returns:
        frame (np.ndarray): 繪製後畫面。
        current_name (str): 辨識出的人名，可能為 Unknown 或 No face。
    """
    now = time.time()
    rgb_frame = frame[:, :, ::-1]  # OpenCV 是 BGR，face_recognition 用 RGB
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    current_name = "No face"
    name = "No face"

    if face_encodings:
        # 只處理第一張臉
        face_encoding = face_encodings[0]
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.4)
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        name = "Unknown"
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_names[best_match_index]
                state["recognized"] = True

        current_name = name

        # 若辨識對象改變則重置時間計數器
        if current_name != state["last_name"]:
            state["elapsed"] = 0
            state["last_name"] = current_name
        else:
            state["elapsed"] += now - state["last_time"]

        # 畫框與名字
        (top, right, bottom, left) = face_locations[0]
        box_color = (0, 0, 255) if name == "Unknown" else (0, 255, 0)
        cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
        cv2.rectangle(frame, (left, bottom - 20), (right, bottom), box_color, cv2.FILLED)
        cv2.putText(frame, name, (left + 2, bottom - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

    else:
        current_name = "No face"
        if current_name != state["last_name"]:
            state["elapsed"] = 0
            state["last_name"] = current_name

        cv2.putText(frame, "無人臉", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # 顯示辨識狀態
    elapsed = state["elapsed"]
    if current_name == "No face":
        title_text = " No Face"
        title_color = (200, 200, 200)
    elif current_name == "Unknown":
        title_text = f"Unknown... {elapsed:.1f} s"
        title_color = (0, 0, 255)
    else:
        title_text = f"passing ... {elapsed:.1f} s"
        title_color = (0, 255, 0)

    cv2.putText(frame, title_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, title_color, 2, cv2.LINE_AA)

    state["last_time"] = now
    return frame, current_name
