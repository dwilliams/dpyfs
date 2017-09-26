#!/usr/bin/env python3

### IMPORTS ############################################################################################################
import hashlib
import logging
import math
import re
import os

from flask import Flask, abort, jsonify, request, send_from_directory, stream_with_context, Response
from werkzeug.utils import secure_filename

### GLOBALS ############################################################################################################
app = Flask(__name__)

MAX_CHUNK_SIZE = 1048576 # 1MB Max chunk size

test_file_uploads = {}

### FUNCTIONS ##########################################################################################################
@app.route('/')
def hello():
    return app.send_static_file('index.html')

@app.route('/img/<path:path>')
def send_imgs(path):
    return send_from_directory('static/img', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('static/js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('static/css', path)

@app.route('/cors/<path:path>')
def send_cors(path):
    return send_from_directory('static/cors', path)

@app.route('/download/')
def list_files():
    filename_list = list(test_file_uploads.keys())
    return jsonify(filename_list)

@app.route('/download/<path:path>')
def handle_download(path):
    # FIXME: Allow 'Range' requests to grab specific parts of files.
    file_to_send = test_file_uploads[secure_filename(path)]
    def generate():
        for i in range(file_to_send['chunk_count']):
            # NOTE: This is where I'd go get the chunks from the storage providers
            yield file_to_send['chunks'][i]['data']
    response = Response(generate(), mimetype='application/octet-stream')
    response.headers['Content-Length'] = file_to_send['size']
    return response

@app.route('/upload/', methods = ['POST'])
def handle_upload():
    print("Request Headers: {}".format(request.headers))
    print("Request Args: {}".format(request.args))
    print("Request Form Data: {}".format(request.form))
    print("Request File Data: {}".format(request.files))
    
    # check if the post request has the file part
    if 'files[]' not in request.files:
        print('No file part')
        abort(400)
    upload_file = request.files['files[]']
    
    # Grab the filename of the upload
    upload_file_name = secure_filename(upload_file.filename)
    print("Filename: {}".format(upload_file_name))
    
    # Check the filename
    if upload_file_name == '':
        abort(400)
    
    # Get file data out of the file list
    file_data = {}
    file_new = True
    if upload_file_name in test_file_uploads:
        file_data = test_file_uploads[upload_file_name]
        file_new = False
    
    # Parse the Content-Range header, which has the following form:
    # Content-Range: bytes 0-524287/2000000
    content_range_header = request.headers.get('Content-Range')
    print("Content-Range Header: {}".format(content_range_header))
    if content_range_header:
        # Chunked upload, so process accordingly
        content_range_split = re.findall(r"[\w']+", content_range_header)
        print("Content-Range Split: {}".format(content_range_split))
        
        content_range_start = int(content_range_split[1])
        content_range_end = int(content_range_split[2])
        content_range_size = int(content_range_split[3])
        print("Content-Range Start: {}, End: {}, Size: {}".format(content_range_start, content_range_end, content_range_size))
        
        # Calculate the size of the chunk and make sure it's not too big
        content_range_chunk_size = content_range_end + 1 - content_range_start
        print("Content-Range Chunk Size: {}".format(content_range_chunk_size))
        if content_range_chunk_size > MAX_CHUNK_SIZE:
            abort(400)
        
        upload_blob = upload_file.read()
        upload_blob_size = len(upload_blob)
        if content_range_chunk_size != upload_blob_size:
            abort(400)
        
        # Make sure the start of the chunk lands on a chunk boundary
        if content_range_start % MAX_CHUNK_SIZE != 0:
            abort(400)
        
        # Calc the total number of chunks and current chunk number
        content_range_chunk_count = math.ceil(content_range_size / MAX_CHUNK_SIZE)
        print("Content-Range Chunk Count: {}".format(content_range_chunk_count))
        content_range_chunk_number = int(content_range_start / MAX_CHUNK_SIZE)
        print("Content-Range Chunk Number: {}".format(content_range_chunk_number))
        
        # FIXME: Check if file exists and if blob has already been uploaded.
        
        # Save needed values
        # FIXME: Should this allow the chunks to be updated without deleting file?
        if file_new:
            file_data['size'] = content_range_size
            file_data['chunk_count'] = content_range_chunk_count
            file_data['chunks'] = {}
        file_data['chunks'][content_range_chunk_number] = {
            'size': upload_blob_size,
            'sha512': hashlib.sha512(upload_blob).hexdigest(),
            'data': upload_blob
        }
        
    else:
        # Single chunk upload
        # Read in the blob and gather some information
        upload_file_blob = upload_file.read()
        upload_file_size = len(upload_file_blob)
        print("Uploaded BLOB size: {}".format(upload_file_size))
        
        # Save file
        # FIXME: Should this allow the file to be updated without deleting?
        if file_new:
            file_data['size'] = upload_file_size
            file_data['chunk_count'] = 1
            file_data['chunks'] = {}
            file_data['chunks'][0] = {
                'size': upload_file_size,
                'sha512': hashlib.sha512(upload_file_blob).hexdigest(),
                'data': upload_file_blob
            }
        else:
            abort(409)
    
    # Save the file_data back to the in memory list
    test_file_uploads[upload_file_name] = file_data
    
    # Print stuff
    for store_file_name, store_file in test_file_uploads.items():
        print("Filename: {}".format(store_file_name))
        print("  Chunk Count: {}/{}".format(len(store_file['chunks']), store_file['chunk_count']))
    
    # Return chuck status
    result = {'files': []}
    result['files'].append({
            'name': upload_file_name,
            'size': file_data['size'],
            'url': "download/{}".format(upload_file_name)
    })
    return jsonify(result)

### CLASSES ############################################################################################################

### MAIN ###############################################################################################################
def main():
    os.environ['DEBUG'] = 'true'
    
    logging.basicConfig(level=logging.DEBUG)
    
    app.run(debug=True, host='0.0.0.0', port=8080)

if __name__ == "__main__":
    main()
