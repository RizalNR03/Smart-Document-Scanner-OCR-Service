// app/enhance.cpp
#include <cstdint>

extern "C" {
    // Menaikkan ketajaman tulisan hitam di atas kertas putih secara linier via array pointer
    void binarize_and_sharpen(uint8_t* data, int width, int height, int channels) {
        int total_bytes = width * height * channels;
        for (int i = 0; i < total_bytes; i++) {
            // Formula peningkatan kontras ekstrem
            int v = data[i];
            if (v < 110) v = v * 0.7;        // Bagian gelap/tulisan dibuat makin gelap
            else v = v * 1.2;                // Bagian terang/kertas dibuat makin putih
            
            if (v > 255) v = 255;
            if (v < 0) v = 0;
            data[i] = (uint8_t)v;
        }
    }
}