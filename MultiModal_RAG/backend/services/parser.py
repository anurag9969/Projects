import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from typing import List, Dict


class PDFParser:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_text(self) -> List[Dict]:
        """
        Extract text and OCR from images page by page.
        Returns structured list:
        [
            {
                "page": 1,
                "text": "...",
                "content_type": "text+image"
            }
        ]
        """

        document = fitz.open(self.file_path)
        pages = []

        for page_number in range(len(document)):
            page = document[page_number]

            # Extract normal text
            text_content = page.get_text("text")

            # Extract images
            image_list = page.get_images(full=True)

            ocr_text = ""

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = document.extract_image(xref)
                image_bytes = base_image["image"]

                image = Image.open(io.BytesIO(image_bytes))

                try:
                    extracted_text = pytesseract.image_to_string(image)
                    ocr_text += "\n" + extracted_text.strip()
                except Exception:
                    continue

            combined_text = (text_content or "") + "\n" + ocr_text

            if combined_text.strip():
                pages.append({
                    "page": page_number + 1,
                    "text": combined_text.strip(),
                    "content_type": "text+image" if ocr_text else "text"
                })

        document.close()

        return pages
