#!/usr/bin/env python3

# Running for dev: gunicorn --reload 'dpyfs_storage.app:get_app()'

### IMPORTS ###
import io
import os
import uuid
import mimetypes

import falcon

from dpyfs.object_stores import ChunkingObjectStore

### GLOBALS ###
CHUNK_SIZE_BYTES = 64 * 1024 # 64K
CONFIG_DIR = os.path.abspath("./etc/dpyfs/") # Fix these later

# Storage Server List
# These are the servers that store chunks.
STORAGE_DUPLICATION_FACTOR=1
STORAGE_SERVERS = [
    'localhost:8081',
    #'localhost:8082',
    #'localhost:8083'
]

### FUNCTIONS ###
def get_chunk_duplication_factor():
    if STORAGE_DUPLICATION_FACTOR < 1:
        return 1
    if len(STORAGE_SERVERS) < STORAGE_DUPLICATION_FACTOR:
        return len(STORAGE_SERVERS)
    return STORAGE_DUPLICATION_FACTOR

def create_app(chunk_store):
    app = falcon.API()
    
    app.add_route('/', RootResource())
    app.add_route('/object', ObjectResource())
    return app

def get_app():
    return create_app()

### CLASSES ###
class RootResource(object):
    # This is the root of the webserver.  Initially, just redirect to info.  Later, maybe
    def on_get(self, req, resp):
        resp.body = "Hello dpyfs_director!".encode('utf-8')
        resp.status = falcon.HTTP_OK

class ObjectResource(object):
    def __init__(self):
        pass
    
    # on_get: retrieve record of chunks, retrieve chunks from storage server, stream object (chunks in the correct order)
    # on_post: split object stream into chunks, store chunks on storage servers, record locations of chunks
    def on_post(self, req, resp):
        resp.body = "Hello dpyfs_director!".encode('utf-8')
        resp.status = falcon.HTTP_OK
