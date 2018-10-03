#!/usr/bin/env python3

### IMPORTS ###
import os
import requests

### GLOBALS ###

### FUNCTIONS ###
def test_post_data_chunk_saved():
    # NOTE: An integration test should test the post, then the get.  Testing the underlying filesystem should for a
    #       unittest with a filesystem mock.

    # file_save_prefix = '/tmp/data/'
    # location_prefix = '/data/'
    # fake_image_bytes = b'fake-image-bytes'

    # response = requests.post('http://localhost:8000/data/', data=fake_image_bytes)

    # assert response.status_code == 201 # HTTP_CREATED
    # location = response.headers['location']
    # assert location.startswith(location_prefix)
    # chunk_name = location.replace(location_prefix, '')

    # file_path = os.path.join(file_save_prefix, chunk_name)
    # with open(file_path, 'rb') as chunk_file:
        # assert chunk_file.read() == fake_image_bytes

    # os.remove(file_path)
    pass

### CLASSES ###
