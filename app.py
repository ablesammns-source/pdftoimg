from flask import Flask, render_template, request, send_file
from pdf2image import convert_from_path
import os
import tempfile
import zipfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'pdf_file' not in request.files:
        return "No file uploaded", 400

    pdf_file = request.files['pdf_file']
    output_format = request.form.get('format', 'png')

    if pdf_file.filename == '':
        return "No file selected", 400

    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, pdf_file.filename)
        pdf_file.save(pdf_path)

        # Convert PDF to images
        images = convert_from_path(pdf_path)

        image_paths = []
        for i, img in enumerate(images, start=1):
            out_path = os.path.join(tmpdir, f"page_{i}.{output_format}")
            img.save(out_path, output_format.upper())
            image_paths.append(out_path)

        # Zip all output images
        zip_path = os.path.join(tmpdir, "converted_images.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for path in image_paths:
                zipf.write(path, os.path.basename(path))

        return send_file(zip_path, as_attachment=True, download_name='converted_images.zip')

if __name__ == '__main__':
    app.run(debug=True)
