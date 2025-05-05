from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from threading import Thread
import time
from scour.scour import scourString
import os
from converter import convert_pdf_to_svg, convert_to_png, convert_to_jpg, convert_to_webp
from rename_organize import rename_and_organize_files

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = {
    'pdf': 'uploads/pdf',
    'jpg': 'uploads/jpg',
    'jpeg': 'uploads/jpeg',
    'png': 'uploads/png',
    'svg': 'uploads/svg',
    'webp': 'uploads/webp'
}
OUTPUT_FOLDER = {
    'svg': 'outputs/svg',
    'png': 'outputs/png',
    'jpg': 'outputs/jpg',
    'webp': 'outputs/webp'
}
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'svg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 限制

# 确保目录存在
for folder in UPLOAD_FOLDER.values():
    os.makedirs(folder, exist_ok=True)
for folder in OUTPUT_FOLDER.values():
    os.makedirs(folder, exist_ok=True)

# 辅助函数：检查文件扩展名
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 路由：主页
@app.route('/')
def index():
    all_files = []
    for folder in app.config['OUTPUT_FOLDER'].values():
        files = [os.path.join(folder, f) for f in os.listdir(folder) if not f.startswith('.')]
        all_files.extend(files)
    return render_template('index.html', svg_files=all_files)

# 路由：上传 PDF
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    files = request.files.getlist('files')
    if not files:
        return jsonify({'message': 'No files selected'}), 400

    formats = request.form.getlist('formats')
    if not formats:
        return jsonify({'message': 'No formats selected'}), 400

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if '.' in filename:
                ext = filename.rsplit('.', 1)[1].lower()
                if ext in app.config['UPLOAD_FOLDER']:
                    upload_folder = app.config['UPLOAD_FOLDER'][ext]
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                else:
                    print(f"Unsupported file type: {ext}")
                    continue
            else:
                print(f"File {filename} has no extension")
                continue

            # Rename and organize the uploaded file
            renamed_files = rename_and_organize_files(upload_folder)

            # Iterate through the renamed files and convert them
            for renamed_file in renamed_files:
                renamed_filename = os.path.basename(renamed_file)
                if 'svg' in formats:
                    thread = Thread(target=convert_pdf_to_svg, args=(renamed_file, app.config['OUTPUT_FOLDER'], renamed_filename))
                    thread.start()
                if 'png' in formats:
                    thread = Thread(target=convert_to_png, args=(renamed_file, app.config['OUTPUT_FOLDER'], renamed_filename))
                    thread.start()
                if 'jpg' in formats:
                    thread = Thread(target=convert_to_jpg, args=(renamed_file, app.config['OUTPUT_FOLDER'], renamed_filename))
                    thread.start()
                if 'webp' in formats:
                    thread = Thread(target=convert_to_webp, args=(renamed_file, app.config['OUTPUT_FOLDER'], renamed_filename))
                    thread.start()

    return jsonify({'message': 'Conversion started successfully'})

# 路由：下载 SVG
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

# 函数：将 PDF 转换为 SVG
def convert_pdf_to_svg(file_path, output_folder, filename):
    pass

# 函数：将 PDF 转换为 PNG
def convert_to_png(file_path, output_folder, filename):
    pass

# 函数：将 PDF 转换为 JPG
def convert_to_jpg(file_path, output_folder, filename):
    pass

# 函数：将 PDF 转换为 WEBP
def convert_to_webp(file_path, output_folder, filename):
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3010, debug=True)
