import tkinter as tk
from facemodule.detector import run_face_recognition
from speechmodule import start_process as start_speech_recognition
import cv2
import time

root = tk.Tk()
root.title("智慧辨識系統")

result_var = tk.StringVar()
label = tk.Label(
    root,
    textvariable=result_var,
    font=("Helvetica", 18, "bold"),
    fg="#2c3e50",
    bg="#f0f4f7",
    pady=10
)
label.pack(pady=20)

def update_result(text):
    result_var.set(text)
from PIL import Image, ImageTk

canvas = tk.Canvas(root, width=320, height=240)
canvas.pack(pady=10)

def show_image(frame):
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = img.resize((320, 240))
    imgtk = ImageTk.PhotoImage(image=img)
    canvas.imgtk = imgtk
    canvas.create_image(0, 0, anchor="nw", image=imgtk)

# 注入語音辨識模組的結果回調
import speechmodule.recorder as recorder
recorder.result_callback = update_result

status_var = tk.StringVar(value="🟡 系統待命中...")
status_label = tk.Label(root, textvariable=status_var, font=("Arial", 12), fg="gray", bg="#f0f4f7")
status_label.pack(pady=5)

def on_face_button_click():
    status_var.set("🔍 臉部辨識中...")
    name, frame = run_face_recognition()
    if name == "Unknown":
        update_result("陌生人出現")
    elif name == "No face":
        update_result("沒有偵測到人臉")
    else:
        update_result(f"歡迎：{name}")
    status_var.set("✅ 臉部辨識完成")
    show_image(frame)

def start_speech_recognition():
    status_var.set("🎙️ 語音辨識中...")
    recorder.start_process()  # 原本功能

btn_style = {
    "bg": "#2ecc71",
    "fg": "white",
    "activebackground": "#27ae60",
    "activeforeground": "white",
    "relief": "flat",
    "overrelief": "groove",       # 滑鼠懸停時的邊框樣式
    "highlightthickness": 0,      # 移除邊框高亮
    "bd": 0,
    "padx": 20,
    "pady": 10,
    "font": ("Helvetica", 14, "bold")
}


# 臉部辨識按鈕
btn_face = tk.Button(root, text="👤 臉部辨識", command=on_face_button_click, **btn_style)
btn_face.pack(pady=10)

# 語音辨識按鈕
btn_voice = tk.Button(root, text="🎙️ 語音辨識", command=start_speech_recognition, **btn_style)
btn_voice.pack(pady=10)
def on_enter(e):
    e.widget['background'] = '#58d68d'
def on_leave(e):
    e.widget['background'] = '#2ecc71'
btn_face.bind("<Enter>", on_enter)
btn_face.bind("<Leave>", on_leave)
btn_voice.bind("<Enter>", on_enter)
btn_voice.bind("<Leave>", on_leave)
root.mainloop()
