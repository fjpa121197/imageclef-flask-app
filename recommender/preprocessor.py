import tensorflow as tf
import numpy as np
import os
import logging


class Preprocessor():
    """ 
    Preprocessor class that handles the preprocessing of images based on steps used during training,
    the image target size is automatically set to (224,224). The images then is converted into array
    and then each pixel value is preprocessed using densenet preprocess_input function.
    """

    def __init__(self):
        self.target_size = (224,224)
        self.upload_folder = 'temp/uploads/'
        self.X = []

    def _transform_image(self, img):
        """
        Transforms a matrix of pixel values, it scales the values into a range of 0 and 1, and the values
        are normalized with respect to the ImageNet dataset.
        """

        preprocessed_img = tf.keras.applications.densenet.preprocess_input(img)
        self.X.append(preprocessed_img)
        self.X = np.array(self.X)

        return self.X


    def load_image(self, filename):
        """Function that loads an image based on the file name, and transforms into a matrix"""

        try:
            if filename.startswith('static/img/img_'):
                path_to_image = filename
            else:
                path_to_image = os.path.join(self.upload_folder, filename)
                
            img = tf.keras.preprocessing.image.load_img(path = path_to_image, target_size = self.target_size)
            img = tf.keras.preprocessing.image.img_to_array(img)
        except Exception as e:
            logging.error('Error during image loading, error message: %s' %e)

        return self._transform_image(img)

    
