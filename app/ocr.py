# app/ocr.py
import easyocr

class OCREngine:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)

    def extract_text(self, image):
        # detail=0 mengembalikan list string teks langsung
        results = self.reader.readtext(image, detail=0)
        # GABUNGKAN MENGGUNAKAN NEWLINE KEMBALI AGAR PARSER TAHU PERBEDAAN BARIS TULISAN
        return "\n".join(results)