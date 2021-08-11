import tensorflow as tf
from .backend.aws_s3 import S3
import os
import logging

# Download trained model (feature extractor) that is located in S3 bucket.
# The trained model could be included within models directory by default but
# It is bigger than suggest maximum object size by Github
if os.path.exists(r'recommender\models\feature_extractor.h5'):
    pass
else:
    S3().download_object('fine-tuned-model-224-densenet121-2021.h5', 
                         r'recommender\models\feature_extractor.h5')

# Model is loaded outside the class so it gets initalized before an actual user makes a request,
# which reduces the waiting time (it is ready before the request)
MODEL = tf.keras.models.load_model(r'recommender\models\feature_extractor.h5')

class FeatureExtractor():
    """
    FeatureExtractor class in charge of transforming preprocessed image (matrix) into a 1-d vector.
    A Densenet-121 fine-tuned model is being used, which has been trained with the ImageCLEFmed concept
    detection task (2021) dataset.

    """

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
