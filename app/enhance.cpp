#include <cstdint>

extern "C" {
    void binarize_and_sharpen(uint8_t* data, int width, int height, int channels) {
        int total_bytes = width * height * channels;
        for (int i = 0; i < total_bytes; i++) {
            int v = data[i];
            if (v < 110) v = v * 0.7;        
            else v = v * 1.2;               
            
            if (v > 255) v = 255;
            if (v < 0) v = 0;
            data[i] = (uint8_t)v;
        }
    }
}