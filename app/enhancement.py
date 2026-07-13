# app/enhancement.py
import cv2
import ctypes
import os
import numpy as np

class ImageEnhancer:
    def __init__(self):
        # Jalur shared library hasil kompilasi g++
        lib_path = os.path.abspath("./libenhance.so")
        if os.path.exists(lib_path):
            self.c_lib = ctypes.CDLL(lib_path)
            self.c_lib.binarize_and_sharpen.argtypes = [
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int
            ]
        else:
            self.c_lib = None

    def enhance(self, warped_image):
        # Naikkan kejelasan gambar dasar dengan OpenCV terlebih dahulu
        gray = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
        enhanced_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        # Panggil fungsi manipulasi pixel C++ jika library tersedia
        if self.c_lib:
            h, w, c = enhanced_bgr.shape
            data_ptr = enhanced_bgr.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
            self.c_lib.binarize_and_sharpen(data_ptr, w, h, c)

        return enhanced_bgr