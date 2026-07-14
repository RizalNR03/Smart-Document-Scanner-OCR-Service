import easyocr

class OCREngine:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)

    def extract_text(self, image):
        results = self.reader.readtext(image, detail=0)
        return "\n".join(results)