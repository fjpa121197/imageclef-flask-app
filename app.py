from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from flask.helpers import send_from_directory
from werkzeug.utils import secure_filename
import umls_api
import logging
from recommender.recommender import Recommender
 
app = Flask(__name__)

UPLOAD_FOLDER = 'temp/uploads/'
app.secret_key = 'pachispachis'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
     

def clean_results(output_data):
    """ formula to clean output_data dictionary"""
    results = []
    for concept, desc in zip(output_data["body"]["concepts"], output_data["body"]["description_concepts"]):
        results.append(f'{concept}: {desc}')
    return results

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
        """ run recommend_cuis and render_home with result variables"""
        results = clean_results(recommend_cuis(filename))
        return render_template('home.html', filename=filename, results=results)
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

    try:
        predicted_cuis = Recommender(filename).recommend_cuis()
        logging.warning('Concepts for image %s predicted succesfully' %filename)
        cuis_description = []

        for concept in predicted_cuis:
            try:
                resp = umls_api.API(api_key = '957ee32c-93a0-4151-83d2-ad19eee77242').get_cui(cui = concept)
                cuis_description.append(resp['result']['name'])
            except:
                logging.warning('UMLS API is unavailable for concept: %s' %concept)
     
        return_data = {
        "concepts": predicted_cuis,
        "description_concepts": cuis_description
        }

        print(return_data)

        output_data = {
        'header': {
            'statusCode': 200
        },
        'body': return_data
        }
        return output_data
    except:
        logging.error('Recommendation error', exc_info=True)

    return output_data

@app.route('/image_delete/<filename>')
def delete_image(filename):

    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return "ok"
 
if __name__ == "__main__":
    logging.basicConfig(
                    format='%(asctime)s %(msecs)d-%(levelname)s - %(message)s', 
                    datefmt='%d-%b-%y %H:%M:%S %p' ,
                    level=logging.INFO)
    app.run(debug=True)
