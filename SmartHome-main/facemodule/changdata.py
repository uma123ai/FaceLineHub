import os
import face_recognition
import numpy as np

WHITELIST_DIR = os.path.join(os.path.dirname(__file__), "face")
FACEDATA_DIR = os.path.join(os.path.dirname(__file__), "facedata")

os.makedirs(FACEDATA_DIR, exist_ok=True)

def generate_facedata():
    for filename in os.listdir(WHITELIST_DIR):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            name = os.path.splitext(filename)[0]
            image_path = os.path.join(WHITELIST_DIR, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                encoding = encodings[0]
                np.save(os.path.join(FACEDATA_DIR, name + ".npy"), encoding)
                print(f" 儲存 {name} 向量成功")
            else:
                print(f" 無法從 {filename} 擷取人臉向量")

if __name__ == "__main__":
    generate_facedata()