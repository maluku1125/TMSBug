import cv2
import numpy as np
import pytesseract

import io
from google.cloud import vision

# 建立 Google Cloud Vision 物件
client = vision.ImageAnnotatorClient()

# 讀取圖片
with io.open("C:\\Users\\User\\Desktop\\222.jpg", "rb") as image_file:
    image = image_file.read()

# 進行文字辨識
text_annotations = client.text_detection(image=image)

# 列印文字辨識結果
for text_annotation in text_annotations.text_annotations:
    print(text_annotation.description)