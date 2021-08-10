import os
import boto3


class S3():
    
    def __init__(self):

        self._bucket_name = 'imageclef-flask-app'
        self._s3 = boto3.client('s3')

    def download_object(self, s3_object_name, saved_object_name):

        return self._s3.download_file(self._bucket_name, s3_object_name, saved_object_name)
        

