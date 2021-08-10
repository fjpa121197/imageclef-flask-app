from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from flask.helpers import send_from_directory
from werkzeug.utils import secure_filename

from recommender.recommender import Recommender
 
app = Flask(__name__)
 
UPLOAD_FOLDER = 'temp/uploads/'
app.secret_key = 'pachispachis'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     
 
@app.route('/')
def home():
    return render_template('home.html')
 
@app.route('/', methods=['POST'])
def upload_image():
    """ Function that handles image upload"""

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        flash('Image successfully uploaded!')
        return render_template('home.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg')
        return redirect(request.url)
 

@app.route('/display/<filename>')
def display_image(filename):
    """Function that display image upload by user, to be used within html file"""
    #print('display_image filename: ' + filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/recommend_cuis/<filename>')
def recommend_cuis(filename):

    predicted_cuis = Recommender(filename).recommend_cuis()

    print(predicted_cuis)
    

    return "ok"


@app.route('/image_delete/<filename>')
def delete_image(filename):

    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return "ok"
 
if __name__ == "__main__":
    app.run(debug=True)