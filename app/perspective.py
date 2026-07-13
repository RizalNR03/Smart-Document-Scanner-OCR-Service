# app/perspective.py
import cv2
import numpy as np

class PerspectiveTransformer:
    def order_points(self, pts):
        # Mengurutkan 4 titik secara konsisten: [top-left, top-right, bottom-right, bottom-left]
        pts = pts.astype("float32")
        rect = np.zeros((4, 2), dtype="float32")

        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)] # Top-left memiliki jumlah x+y terkecil
        rect[2] = pts[np.argmax(s)] # Bottom-right memiliki jumlah x+y terbesar

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)] # Top-right memiliki selisih y-x terkecil (atau x-y terbesar)
        rect[3] = pts[np.argmax(diff)] # Bottom-left memiliki selisih y-x terbesar

        return rect

    def transform(self, original_image, box, ratio):
        if box is None:
            # Jika tidak terdeteksi kotak, kembalikan gambar asli sebagai bentuk toleransi kegagalan
            return original_image, 0.0

        # Kembalikan koordinat kotak ke skala gambar asli menggunakan ratio
        pts = box * ratio
        rect = self.order_points(pts)
        (tl, tr, br, bl) = rect

        # Hitung lebar maksimal kartu nama baru
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        # Hitung tinggi maksimal kartu nama baru
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # Target dimensi hasil scan top-down view
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        # Hitung matriks transformasi perspektif dan terapkan
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(original_image, M, (maxWidth, maxHeight))

        # Hitung perkiraan sudut rotasi dasar untuk dimasukkan ke metadata JSON
        angle = np.arctan2(tr[1] - tl[1], tr[0] - tl[0]) * 180 / np.pi

        return warped, round(angle, 2)