from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from PIL import Image
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_image(input_path, output_path, format):
    with Image.open(input_path) as img:
        img.save(output_path, format=format.upper())

@app.route('/')
def index():
    return render_template('index.html')

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
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

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
            "download_url": f"/download/{output_filename}"
        })

    return jsonify({"error": "不支持的文件类型"}), 400

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=3010)