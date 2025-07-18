import cv2
import time
from .facefunction import load_facedata, process_frame, save_log, save_unknown_image

def run_face_recognition(timeout=3, log_path="log.xlsx", show_window=True):
    """
    執行臉部辨識主流程（攝影機開啟、即時比對、紀錄 Log）。

    Args:
        timeout (int): 通過或陌生人偵測持續時間（秒）。
        log_path (str): Log 檔儲存位置。
        show_window (bool): 是否顯示即時畫面。

    Returns:
        name (str): 最後辨識結果（Unknown, No face, 或人名）。
        frame (np.ndarray or None): 對應畫面影像，可供儲存。
    """
    print("🔍 [FaceRec] Loading known face vectors...")
    known_encodings, known_names = load_facedata()

    print("📷 [FaceRec] Starting camera...")
    cap = cv2.VideoCapture(0)

    state = {
        "elapsed": 0,
        "last_time": time.time(),
        "last_name": "No face",
        "recognized": False
    }

    last_frame = None
    current_name = "No face"

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        last_frame = frame.copy()
        frame, current_name = process_frame(frame, known_encodings, known_names, state)

        if show_window:
            cv2.imshow("Face Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("❌ [FaceRec] Manual quit")
                break

        # 如果通過，紀錄 Log
        if state["recognized"] and current_name not in ["Unknown", "No face"] and state["elapsed"] >= timeout:
            print(f"✅ [FaceRec] Recognized: {current_name}")
            save_log(current_name, "Success", excel_path=log_path)
            cap.release()
            cv2.destroyAllWindows()
            return current_name, last_frame

        # 若是陌生人停留過久，儲存圖像與 Log
        if current_name == "Unknown" and state["elapsed"] >= timeout:
            print("⚠️ [FaceRec] Unknown timeout")
            save_log("Unknown", "Unknown", excel_path=log_path)
            if last_frame is not None:
                save_unknown_image(last_frame)
            cap.release()
            cv2.destroyAllWindows()
            return "Unknown", last_frame

    cap.release()
    cv2.destroyAllWindows()
    return "No face", None
