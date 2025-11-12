import os
import requests
import torch
from io import BytesIO
from PIL import Image
from transformers import BlipProcessor, BlipForQuestionAnswering
from config import device

# Tải mô hình BLIP
try:
    vqa_processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
    vqa_model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base").to(device)
    print("Đã tải mô hình BLIP VQA.")
except Exception as e:
    vqa_processor, vqa_model = None, None
    print(f"Lỗi tải BLIP: {e}")

def analyze_image_tool(image_path: str, question: str) -> str:
    """Phân tích hình ảnh từ link hoặc file local."""
    if not vqa_model or not vqa_processor:
        return "Lỗi: Mô hình VQA không khả dụng."

    try:
        if image_path.lower().startswith(("http://", "https://")):
            response = requests.get(image_path, stream=True, timeout=10)
            if response.status_code != 200:
                return f"Lỗi tải ảnh (HTTP {response.status_code})"
            image = Image.open(BytesIO(response.content)).convert("RGB")
        else:
            if not os.path.exists(image_path):
                return f"Không tìm thấy ảnh: {image_path}"
            image = Image.open(image_path).convert("RGB")

        inputs = vqa_processor(image, question, return_tensors="pt").to(device)
        with torch.no_grad():
            out = vqa_model.generate(**inputs, max_new_tokens=50)
        answer = vqa_processor.decode(out[0], skip_special_tokens=True)
        return f"Kết quả phân tích ảnh: {answer}"

    except Exception as e:
        return f"Lỗi khi xử lý hình ảnh: {e}"
