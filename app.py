from flask import Flask, request, render_template, send_file
import pdf2image
import pytesseract
import os
import io
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

app = Flask(__name__)


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


poppler_path = r'C:\Users\SAVINDU\Desktop\Release-24.08.0-0\poppler-24.08.0\Library\bin'  // my //

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


ocr_result = ""

@app.route('/', methods=['GET', 'POST'])
def index():
    global ocr_result
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return "No file part in the request"
        file = request.files['pdf_file']
        if file.filename == '':
            return "No file selected"
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

          
            pages = pdf2image.convert_from_path(filepath, dpi=300, poppler_path=poppler_path)
            text = ''
            for page in pages:
                text += pytesseract.image_to_string(page, lang='sin')

            ocr_result = text
            return render_template('result.html', text=text)
    return render_template('index.html')


@app.route('/download_docx', methods=['POST'])
def download_docx():
    global ocr_result
    if not ocr_result:
        return "No OCR result to export"
    doc = Document()
    doc.add_paragraph(ocr_result)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name="ocr_result.docx",
                     mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    global ocr_result
    if not ocr_result:
        return "No OCR result to export"
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica", 12)
    y = 800
    for line in ocr_result.splitlines():
        c.drawString(100, y, line)
        y -= 20
        if y < 50: 
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 800
    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True,
                     download_name="ocr_result.pdf",
                     mimetype="application/pdf")

if __name__ == '__main__':
    app.run(debug=True)
