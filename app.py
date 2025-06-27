import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
import steganography

# Konfigurasi
UPLOAD_FOLDER = 'uploads/'
DOWNLOAD_FOLDER = 'downloads/'
ALLOWED_EXTENSIONS = {'png', 'bmp', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.secret_key = 'kunci_rahasia_super_aman' # Ganti dengan kunci rahasia Anda sendiri

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Cek apakah ada file yang di-upload
        if 'image' not in request.files:
            flash('Tidak ada file yang dipilih')
            return redirect(request.url)
        
        file = request.files['image']
        
        if file.filename == '':
            flash('Tidak ada file yang dipilih')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Simpan file yang di-upload sementara
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Cek form mana yang di-submit (Encode atau Decode)
            if 'encode' in request.form:
                secret_text = request.form['secret_text']
                if not secret_text:
                    flash('Teks rahasia tidak boleh kosong untuk di-encode!')
                    return redirect(request.url)
                
                output_filename = 'encoded_' + filename
                # Panggil fungsi encode dari steganography.py
                result_file, message = steganography.encode_image(filepath, secret_text, output_filename)
                
                flash(message)
                if result_file:
                    return render_template('index.html', encoded_image=result_file)

            elif 'decode' in request.form:
                # Panggil fungsi decode dari steganography.py
                decoded_text = steganography.decode_image(filepath)
                return render_template('index.html', decoded_text=decoded_text)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    """Menyediakan link download untuk file hasil encode."""
    return send_from_directory(app.config["DOWNLOAD_FOLDER"], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)