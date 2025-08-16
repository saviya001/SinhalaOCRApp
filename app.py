from flask import Flask, request, render_template
import pdf2image
import pytesseract
import os

app = Flask(__name__)

# ඔබේ Tesseract exe path එක මෙහෙ දාන්න:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ඔබේ poppler bin folder එක මෙහෙ දාන්න:
poppler_path = r'C:\Users\SAVINDU\Desktop\Release-24.08.0-0\poppler-24.08.0\Library\bin'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return "No file part in the request"
        file = request.files['pdf_file']
        if file.filename == '':
            return "No file selected"
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # PDF එකෙන් pages images වලට පරිවර්තනය කරයි
            pages = pdf2image.convert_from_path(filepath, dpi=300, poppler_path=poppler_path)
            text = ''
            for page in pages:
                # සිංහල OCR language එකෙන් text එක ගැනීම
                text += pytesseract.image_to_string(page, lang='sin')

            return render_template('result.html', text=text)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
