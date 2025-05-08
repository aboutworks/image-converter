from PIL import Image
import fitz  # PyMuPDF

def convert_to_webp(input_path, output_path):
    with Image.open(input_path) as img:
        img.save(output_path, 'WEBP')

def convert_to_png(input_path, output_path):
    with Image.open(input_path) as img:
        img.save(output_path, 'PNG')

def convert_to_jpg(input_path, output_path):
    with Image.open(input_path) as img:
        rgb = img.convert('RGB')
        rgb.save(output_path, 'JPEG')

def convert_pdf_to_svg(input_path, output_path):
    # 提取第1页为 SVG
    doc = fitz.open(input_path)
    page = doc.load_page(0)
    svg = page.get_svg_image()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)