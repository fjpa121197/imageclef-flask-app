import tensorflow as tf
from .backend.aws_s3 import S3
import os

if os.path.exists(r'recommender\models\feature_extractor.h5'):
    pass
else:
    S3().download_object('fine-tuned-model-224-densenet121-2021.h5', 
                         r'recommender\models\feature_extractor.h5')

MODEL = tf.keras.models.load_model(r'recommender\models\feature_extractor.h5')

class FeatureExtractor():

    def __init__(self, preprocessed_image, output_layer = -2):

        self.preprocessed_image = preprocessed_image
        self.output_layer = output_layer
        self._model = MODEL
    
    
    def _define_layer_output(self):

        layer_output = tf.keras.backend.function([self._model.layers[0].input], 
                                                 [self._model.layers[self.output_layer].output])

        return layer_output

    def extracted_features(self):

        get_layer_output = self._define_layer_output()
        features = get_layer_output([self.preprocessed_image])[0]
        features = features.flatten()

        return features
