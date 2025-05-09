from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from PIL import Image
import os
import pythoncom
import win32com.client

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
DWG_FOLDER = os.path.join(UPLOAD_FOLDER, 'dwg')
PDF_FOLDER = os.path.join(OUTPUT_FOLDER, 'pdf')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# 创建必要目录
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DWG_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_image(input_path, output_path, format):
    with Image.open(input_path) as img:
        img.save(output_path, format=format.upper())

# ✅ DWG 转 PDF
def convert_dwg_to_pdf(dwg_path, pdf_output_path):
    pythoncom.CoInitialize()
    acad = win32com.client.Dispatch("AutoCAD.Application")
    acad.Visible = False
    doc = acad.Documents.Open(dwg_path)
    doc.SetVariable("BACKGROUNDPLOT", 0)

    dsd_path = os.path.splitext(dwg_path)[0] + ".dsd"
    pdf_output_dir = os.path.dirname(pdf_output_path)

    dsd_content = f"""[DWF6Version]
Ver=1
[DWF6MinorVersion]
MinorVer=1
[Sheet1]
DWG={dwg_path}
Layout=*
Setup=
OriginalSheetPath={dwg_path}
Has PlotStyles=0
[Target]
Type=6
DWF={pdf_output_path}
OUT={pdf_output_dir}
PWD=
[AutoCAD Block Data]
IncludeLayer=TRUE
PromptForDwfName=FALSE
RememberSheetSet=FALSE
"""

    with open(dsd_path, "w") as f:
        f.write(dsd_content)

    acad.Publish.PublishToWeb(dsd_path)
    doc.Close(False)
    acad.Quit()
    pythoncom.CoUninitialize()

# 首页展示
@app.route('/')
def index():
    all_files = []
    for subdir in os.listdir(OUTPUT_FOLDER):
        subdir_path = os.path.join(OUTPUT_FOLDER, subdir)
        if os.path.isdir(subdir_path):
            for file in os.listdir(subdir_path):
                file_path = f"{subdir}/{file}"
                all_files.append(file_path)
    return render_template('index.html', converted_files=all_files)

# 图像转换
@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    convert_type = request.form.get('convert_type')
    if convert_type not in {'webp', 'png', 'jpg'}:
        return jsonify({"error": "无效的转换类型"}), 400

    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}.{convert_type}"
        output_dir = os.path.join(OUTPUT_FOLDER, convert_type)
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)

        try:
            convert_image(input_path, output_path, convert_type)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if os.path.exists(input_path):
                os.remove(input_path)

        return jsonify({
            "message": "转换成功",
            "output_file": output_filename,
            "download_url": f"/download/{convert_type}/{output_filename}"
        })

    return jsonify({"error": "不支持的文件类型"}), 400

# ✅ DWG 转 PDF 路由
@app.route('/dwgtopdf', methods=['POST'])
def dwg_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "没有上传 DWG 文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "未选择文件"}), 400

    if file and file.filename.lower().endswith('.dwg'):
        filename = secure_filename(file.filename)
        dwg_path = os.path.join(DWG_FOLDER, filename)
        file.save(dwg_path)

        base_name = os.path.splitext(filename)[0]
        output_pdf_path = os.path.join(PDF_FOLDER, f"{base_name}.pdf")

        try:
            convert_dwg_to_pdf(dwg_path, output_pdf_path)
        except Exception as e:
            return jsonify({"error": f"转换失败: {e}"}), 500
        finally:
            if os.path.exists(dwg_path):
                os.remove(dwg_path)

        return jsonify({
            "message": "DWG 转换成功",
            "output_file": f"{base_name}.pdf",
            "download_url": f"/download/pdf/{base_name}.pdf"
        })

    return jsonify({"error": "只支持 DWG 文件"}), 400

@app.route('/download/<format>/<filename>')
def download_file(format, filename):
    folder = os.path.join(OUTPUT_FOLDER, format)
    return send_from_directory(folder, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=3010)