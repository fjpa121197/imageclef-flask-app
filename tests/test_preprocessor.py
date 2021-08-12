import os
import unittest
import numpy as np
from recommender.preprocessor import Preprocessor


image_test_path = 'synpic16394.jpg'


class PreprocessorTests(unittest.TestCase):

    def setUp(self):

        self.image_test_path = image_test_path
        self.correct_image_size = 150528 # This is the correct size if image loaded is 224x224
        self.image_test_preprocessed = Preprocessor().load_image(self.image_test_path)


    def test_load_image(self):

        self.assertIsNotNone(self.image_test_preprocessed)

    def test_size_image(self):

        self.assertEqual(self.correct_image_size, self.image_test_preprocessed.size)

    def test_type_preprocessed_image(self):

        self.assertIsInstance(self.image_test_preprocessed, np.ndarray)



