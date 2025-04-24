from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from threading import Thread
import time
from scour.scour import scourString
import os

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = 'uploads/pdfs'
OUTPUT_FOLDER = 'uploads/svgs'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 限制

# 确保目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# 全局变量：存储每个文件的转换进度
progress_status = {}

# 辅助函数：检查文件扩展名
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 路由：主页
@app.route('/')
def index():
    svg_files = os.listdir(app.config['OUTPUT_FOLDER'])
    return render_template('index.html', svg_files=svg_files)

# 路由：上传 PDF
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)
        # 初始化进度为 0
        progress_status[filename] = 0
        # 启动转换线程
        thread = Thread(target=convert_pdf_to_svg, args=(filename,))
        thread.start()
        return render_template('progress.html', filename=filename)
    return redirect(url_for('index'))

# 路由：下载 SVG
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

# 函数：将 PDF 转换为 SVG
def convert_pdf_to_svg(filename):
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    doc = fitz.open(pdf_path)
    total_pages = len(doc)  # 获取总页数
    for page_num in range(total_pages):
        svg_filename = f"{os.path.splitext(filename)[0]}_page{page_num + 1}.svg"
        svg_path = os.path.join(app.config['OUTPUT_FOLDER'], svg_filename)
        page = doc[page_num]
        svg_content = page.get_svg_image()

        # 优化 SVG 内容
        scour_options = {
            "remove_metadata": True,
            "strip_comments": True,
            "shorten_ids": True,
        }
        optimized_svg = scourString(svg_content, options=scour_options)

        # 保存优化后的 SVG
        with open(svg_path, 'w') as svg_file:
            svg_file.write(optimized_svg)

        # 更新进度
        progress_status[filename] = int(((page_num + 1) / total_pages) * 100)

    doc.close()
    # 确保进度为 100%
    progress_status[filename] = 100

# 路由：检查转换进度
@app.route('/progress/<filename>')
def check_progress(filename):
    progress = progress_status.get(filename, 0)  # 获取当前进度
    return jsonify({'status': f'{progress}%'})  # 返回百分比进度

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3010, debug=True)