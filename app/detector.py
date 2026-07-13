# app/detector.py
import cv2
import numpy as np
import imutils

class DocumentDetector:
    def detect(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Gambar tidak ditemukan: {image_path}")

        original = image.copy()
        image = imutils.resize(image, height=700)
        ratio = original.shape[0] / image.shape[0]

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Gunakan Bilateral Filter untuk mempertahankan ketajaman tepi kartu nama
        blurred = cv2.bilateralFilter(gray, 11, 85, 85)
        
        # Gunakan Adaptive Thresholding agar area putih kartu di dalam monitor terisolasi dengan baik
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY_INV, 11, 2)

        # Lakukan pelebaran tepi (Dilation) untuk menyambung struktur kartu nama yang terputus
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(thresh, kernel, iterations=1)

        # Cari kontur
        contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]

        best_box = None
        img_area = image.shape[0] * image.shape[1]

        for contour in contours:
            area = cv2.contourArea(contour)
            
            # ABAIKAN KONTUR JIKA TERLALU BESAR (SEPERTI SELAYAR PENUH) ATAU TERLALU KECIL
            if area > (img_area * 0.90) or area < (img_area * 0.15):
                continue

            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

            # Jika menemukan objek 4 sudut (Kandidat kuat kartu nama persegi)
            if len(approx) == 4:
                best_box = approx.reshape(4, 2)
                break
        
        # Fallback dinamis jika kontur 4 sudut gagal: gunakan bounding rect dari objek terbesar kedua
        if best_box is None and len(contours) > 1:
            for c in contours[1:5]: # Lewati yang pertama karena kemungkinan besar itu tepi luar monitor
                area = cv2.contourArea(c)
                if area > (img_area * 0.85) or area < (img_area * 0.10):
                    continue
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.04 * peri, True)
                if len(approx) == 4:
                    best_box = approx.reshape(4, 2)
                    break
                
                # Jika tidak 4 sudut tapi berbentuk kotak bebas
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                best_box = np.int32(box)
                break

        # Skenario terburuk jika deteksi gagal total, pakai area tengah gambar (safe-crop)
        if best_box is None:
            h, w = image.shape[:2]
            best_box = np.array([
                [int(w*0.05), int(h*0.05)],
                [int(w*0.95), int(h*0.05)],
                [int(w*0.95), int(h*0.95)],
                [int(w*0.05), int(h*0.95)]
            ])

        output = image.copy()
        cv2.drawContours(output, [np.int32(best_box)], -1, (0, 255, 0), 3)

        return output, thresh, best_box, ratio, original