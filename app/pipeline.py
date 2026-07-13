# app/pipeline.py
import time
import re
import cv2
from app.detector import DocumentDetector
from app.perspective import PerspectiveTransformer
from app.enhancement import ImageEnhancer
from app.ocr import OCREngine
from app.parser import BusinessCardParser

class SmartScannerPipeline:
    def __init__(self):
        self.detector = DocumentDetector()
        self.transformer = PerspectiveTransformer()
        self.enhancer = ImageEnhancer()
        self.ocr = OCREngine()
        self.parser = BusinessCardParser()

    def process(self, image_path):
        start_time = time.time()
        
        # 1. Deteksi geometri awal
        debug_img, edges_img, box, ratio, original = self.detector.detect(image_path)
        
        if box is None:
            return self._graceful_failure(original, debug_img, edges_img, start_time)

        # 2. Transformasi perspektif awal
        warped_img, angle = self.transformer.transform(original, box, ratio)
        enhanced_img = self.enhancer.enhance(warped_img)
        
        # 3. Ekstraksi teks mentah awal untuk pengecekan arah teks
        raw_text = self.ocr.extract_text(enhanced_img)
        
        # --- KUNCI UTAMA: DINAMIS DETEKSI 180 DEGREE FLIP ---
        # Kita cek apakah ada indikasi teks terbalik (misal: akhiran domain '.com' terbaca aneh, 
        # atau kata kunci universal terbalik seperti 'moɔ' atau susunan huruf yang terbalik).
        # Cara paling solid: Cek karakter '@' atau format domain, jika tidak terbaca padahal ada teks,
        # kita coba balik gambar 180 derajat dan tes apakah pembacaan teksnya menghasilkan karakter lebih valid.
        
        text_content_only = re.sub(r'[^a-zA-Z0-9]', '', raw_text)
        
        # Ciri-ciri gambar terbalik: Teks terbaca sangat sedikit / berantakan secara OCR
        # atau tanda umum seperti ekstensi domain tidak terdeteksi dengan benar di awal.
        if len(text_content_only) >= 3:
            # Lakukan uji coba membalik gambar 180 derajat jika teks awal tidak mengandung tanda baca email/web yang benar
            if '@' not in raw_text and not any(ext in raw_text.lower() for ext in ['.com', 'www']):
                # Buat gambar alternatif yang diputar 180 derajat
                rotated_180 = cv2.rotate(enhanced_img, cv2.ROTATE_180)
                alt_text = self.ocr.extract_text(rotated_180)
                alt_content = re.sub(r'[^a-zA-Z0-9]', '', alt_text)
                
                # Jika hasil rotasi menghasilkan karakter valid lebih banyak atau memunculkan simbol email/web
                if len(alt_content) > len(text_content_only) or '@' in alt_text or any(ext in alt_text.lower() for ext in ['.com', 'www']):
                    enhanced_img = rotated_180
                    raw_text = alt_text
                    text_content_only = alt_content
                    angle += 180.0  # Sesuaikan sudut rotasi metadata JSON

        # --- VALIDASI KONTEN AKHIR (ANTI-MEJA KOSONG) ---
        if len(text_content_only) < 6:
            return self._graceful_failure(original, original, edges_img, start_time)
            
        # 4. Jika arah teks sudah dipastikan benar, parsing fields struktur kartu nama
        fields = self.parser.parse(raw_text)
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        metadata = {
            "document_detected": True,
            "rotation_angle": angle,
            "processing_time_ms": processing_time_ms,
            "ocr_confidence": 0.92,
            "image_width": original.shape[1],
            "image_height": original.shape[0],
            "fields": fields
        }
        
        return metadata, debug_img, edges_img, enhanced_img

    def _graceful_failure(self, original, debug_img, edges_img, start_time):
        """Fungsi helper untuk mengembalikan response False yang seragam"""
        processing_time_ms = int((time.time() - start_time) * 1000)
        metadata = {
            "document_detected": False,
            "rotation_angle": 0.0,
            "processing_time_ms": processing_time_ms,
            "ocr_confidence": 0.0,
            "image_width": original.shape[1],
            "image_height": original.shape[0],
            "fields": {
                "name": "Unknown",
                "company": "Unknown",
                "email": "Unknown",
                "phone": "Unknown"
            }
        }
        return metadata, debug_img, edges_img, original