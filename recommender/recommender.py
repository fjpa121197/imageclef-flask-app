from .preprocessor import Preprocessor
from .feature_extractor import FeatureExtractor
from .backend.aws_s3 import S3


import pickle
import os
import pandas as pd
import numpy as np
import logging

# Download trained model (fitted k-nn) that is located in S3 bucket.
# The trained model could be included within models directory by default but
# It is bigger than suggest maximum object size by Github

if os.path.exists(r'recommender\models\knn_model.pkl'):
    pass
else:
    S3().download_object('knn_model.pkl', 
                         r'recommender\models\knn_model.pkl')
                    
with open(r'recommender\models\knn_model.pkl', 'rb') as f:
    MODEL = pickle.load(f)



if os.path.exists(r'recommender\models\merged-train-val-concepts.csv'):
    pass
else:
    S3().download_object('merged-train-val-concepts.csv', 
                         r'recommender\models\merged-train-val-concepts.csv')

TAGS_DB = pd.read_csv(r'recommender\models\merged-train-val-concepts.csv', names=['ImageId', 'Tags'], sep='\t')

if os.path.exists(r'recommender\models\train-val-images-features.npy'):
    pass
else:
    S3().download_object('train-val-images-features.npy', 
                         r'recommender\models\train-val-images-features.npy')

FEATURES_DB = np.load(r'recommender\models\train-val-images-features.npy')


class Recommender():

    def __init__(self, filename):
        
        self.filename = filename
        self.preprocessed_image = Preprocessor().load_image(filename)
        self.image_feature_vector = []
        self.db_images_tags = TAGS_DB
        self.knn_model = MODEL
        self.db_images_features = FEATURES_DB

    def _extract_features(self):

        return FeatureExtractor(self.preprocessed_image).extracted_features()



    def recommend_cuis(self):
        """
        Function that is used to recommend concepts to an image given by the user.
        It uses methods that are defined in other two classes: Preprocessor and FeatureExtractor.

        It processess the image first (based on same methods used in training) and
        it then uses a feature extractor deep learning model to transform the image
        from (224,224) matrix to 1-d array of size 1024. 
        
        The 1-d array is then used with a fitted k-nn model (with similar radiological images) 
        to find the most similar image and return those concepts.

        Returns: 1-d list of concepts. Example: ['C0019239', 'C1023566',...]
        """
        try:
            self.image_feature_vector  = self._extract_features()
        except Exception as e:
            logging.error('Error during image feature extraction, error message: %s' %e)

        try:
            closest_image = self.knn_model.kneighbors([self.image_feature_vector], return_distance = True)
    
            can = pd.DataFrame([['synpic'+str(int(self.db_images_features[closest_image[1][0][0]][0])),
                                closest_image[0][0][0]]], columns=['ImageId','can_distance'])

            candidate_image_tags = pd.merge(can, self.db_images_tags, on='ImageId')
            
            candidate_tags = list(set(candidate_image_tags['Tags'][0].split(';')))

            return candidate_tags

        except Exception as e:
            logging.error('Error during concept selection (k-nn model), error message: %s' %e)



        
        


    