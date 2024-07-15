import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io, sys, os
from tqdm import tqdm

def extract_text_from_single_column_with_ocr(pdf_path, header_height=50, footer_height=50):
    # Open the PDF
    document = fitz.open(pdf_path)
    full_text = ""

    for page_num in tqdm(range(document.page_count)):
        page = document.load_page(page_num)
        
        # Render page to an image (300 DPI for better OCR results)
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        # Remove headers and footers by cropping the image
        width, height = img.size
        cropped_img = img.crop((0, header_height, width, height - footer_height))
        
        # Perform OCR on the cropped image
        page_text = pytesseract.image_to_string(cropped_img, lang='chi_sim')
        
        # Add the text from this page to the full text
        full_text += page_text + "\n"

    return full_text

def extract_text_from_columns_with_ocr(pdf_path, dotted_line_width=50, header_height=250, footer_height=200):
    # Open the PDF
    document = fitz.open(pdf_path)
    full_text = ""
    print(f"Extracting {pdf_path}")
    for page_num in tqdm(range(document.page_count)):
        page = document.load_page(page_num)
        
        # Render page to an image (300 DPI for better OCR results)
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        # Remove headers and footers by cropping the image
        width, height = img.size
        cropped_img = img.crop((0, header_height, width, height - footer_height))
        
        # Split the cropped image into left and right columns, excluding the dotted line area
        cropped_width, cropped_height = cropped_img.size
        middle = cropped_width // 2
        left_img = cropped_img.crop((0, 0, middle - dotted_line_width // 2, cropped_height))
        right_img = cropped_img.crop((middle + dotted_line_width // 2, 0, cropped_width, cropped_height))
        
        # Perform OCR on both columns
        left_text = pytesseract.image_to_string(left_img, lang='chi_sim')
        right_text = pytesseract.image_to_string(right_img, lang='chi_sim')
        
        # Combine the text from both columns
        page_text = left_text + "\n" + right_text + "\n"
        full_text += page_text + "\n"

    return full_text

# Specify your PDF file path
pdf_path = sys.argv[1]
output_dir = sys.argv[2]
os.makedirs(output_dir, exist_ok=True)
single=sys.argv[3].lower() in ("true", "1", "yes", "single")
assert os.path.isfile(pdf_path), f"Error: {pdf_path} is not a valid PDF file"

# Extract text using OCR
if single:
    text = extract_text_from_single_column_with_ocr(pdf_path)
else:
    text = extract_text_from_columns_with_ocr(pdf_path)

output_filename = os.path.splitext(os.path.basename(pdf_path))[0] + '.txt'
# Save the text to a file
with open(os.path.join(output_dir, output_filename), "w", encoding="utf-8") as text_file:
    text_file.write(text)

print(f"OCR text extraction complete. Saved to {output_filename}")