from flask import Flask, flash, request, redirect, url_for, render_template
import urllib.request
import os
from flask.helpers import send_from_directory
from werkzeug.utils import secure_filename
import json
import logging
from time import sleep
import datetime
from recommender.recommender import Recommender
from recommender.backend.aws_s3 import S3

app = Flask(__name__)

EXAMPLE_FOLDER = 'static/img/'
UPLOAD_FOLDER = 'temp/uploads/'
app.secret_key = 'pachispachis'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EXAMPLE_FOLDER'] = EXAMPLE_FOLDER
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

@app.route('/health_check')
def health_check():
    return 'ok'
    
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
        return render_template('predict.html', filename=filename, results=results)
    else:
        flash('Allowed image types are - png, jpg, jpeg')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    """Function that display image upload by user, to be used within html file"""

    # print('display_image filename: ' + filename)
    if filename.startswith('img_'):
        return send_from_directory(app.config['EXAMPLE_FOLDER'], filename)
    else:
        return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    # elif filename start with static


@app.route('/recommend_cuis/<filename>')
def recommend_cuis(filename):

    try:
        begin_time_recommendation = datetime.datetime.now()

        predicted_cuis = Recommender(filename).recommend_cuis()

        recommendation_exec_time = datetime.datetime.now() - begin_time_recommendation

        # logging.warning('Concepts for image %s predicted succesfully' %filename)

        cuis_description = []

        for concept in predicted_cuis:
            try:
                cuis_description.append(CUIS_DESC[concept])
            except:
                logging.error('Error retrieving concept description')

        return_data = {
        "concepts": predicted_cuis,
        "description_concepts": cuis_description,
        "recommendation_exec_time": str(recommendation_exec_time)
        }

        logging.warning(return_data)

        output_data = {
        'header': {
            'statusCode': 200
            },
        'body': return_data
        }
        return output_data
    except:
        logging.error('Recommendation error', exc_info=True)

        return "Error"

@app.route('/example/<filename>')
def example(filename):
    if filename.startswith('img_'):
        full_path = f'static/img/{filename}'

    results = clean_results(recommend_cuis(full_path))

    """
    results = clean_results({
        'header': {
            'statusCode': 200
            },
        'body': {'concepts': ['C0411904', 'C1306645'], 'description_concepts': ['Radiography of elbow', 'Plain x-ray']}
        })

    """
    return render_template('predict.html', filename=filename, results=results)

@app.route('/image_delete/<filename>')
def delete_image(filename):
    
    if filename.startswith('img_'):
        pass
    else:
        sleep(0.2)  
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)))

    return "ok"

@app.route('/challenge_description')
def challenge_description():
    return render_template('challenge_description.html')

if __name__ == "__main__":
    logging.basicConfig(
                    format='%(asctime)s %(msecs)d-%(levelname)s - %(message)s', 
                    datefmt='%d-%b-%y %H:%M:%S %p' ,
                    level=logging.INFO)

    
    if os.path.exists(r'recommender\models\concepts-description-2020-2021-images.json'):
        pass
    else:
        S3().download_object('concepts-description-2020-2021-images.json', 
                            r'recommender\models\concepts-description-2020-2021-images.json')
        
        print("Downloaded dict corrected")
        

    with open('recommender\models\concepts-description-2020-2021-images.json','r') as json_file:
        CUIS_DESC = json.load(json_file)
        
    app.run(host='0.0.0.0',port = 80)
