from .preprocessor import Preprocessor
from .feature_extractor import FeatureExtractor
from .backend.aws_s3 import S3


import pickle
import os

if os.path.exists(r'recommender\models\knn_model.pkl'):
    pass
else:
    S3().download_object('knn_model.pkl', 
                         r'recommender\models\knn_model.pkl')

with open(r'recommender\models\knn_model.pkl', 'rb') as f:
    MODEL = pickle.load(f)


class Recommender():

    def __init__(self, filename):

        self.filename = filename
        self.preprocessed_image = Preprocessor().load_image(filename)
        self.image_feature_vector = []

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

        self.image_feature_vector  = self._extract_features()
        closest_image = MODEL.kneighbors([self.image_feature_vector], return_distance = True)
        
        return closest_image
        


    