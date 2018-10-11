#!/usr/bin/env python3

# Running for dev: gunicorn --reload 'dpyfs_storage.app:get_app()'

### IMPORTS ###
import io
import os
import uuid
import mimetypes

import falcon

from dpyfs.chunk_stores.filesystem import ChunkStore

### GLOBALS ###
BLOCK_SIZE_BYTES = 64 * 1024 # 64K
STORAGE_DIR = os.path.abspath("/tmp/data/") # Fix these later
CONFIG_DIR = os.path.abspath("./etc/dpyfs/") # Fix these later

### FUNCTIONS ###
def create_app(chunk_store):
    app = falcon.API()
    
    app.add_route('/', RootResource())
    app.add_route('/info', InfoResource())
    app.add_route('/integritycheck', IntegrityCheckResource())
    app.add_route('/data', DataResource(chunk_store))
    return app

def get_app():
    chunk_store = ChunkStore(storage_path=STORAGE_DIR)
    return create_app(chunk_store)

### CLASSES ###
# Paths:
#   /
#   /info
#   /integritycheck
#   /data/<MD5_hash>/<SHA1_hash>

class RootResource(object):
    # This is the root of the webserver.  Initially, just redirect to info.  Later, maybe
    def on_get(self, req, resp):
        resp.body = "Hello dpyfs!".encode('utf-8')
        resp.status = falcon.HTTP_OK

class InfoResource(object):
    # This is the information page, which contains information such as disk space usage.
    # on_get
    pass

class IntegrityCheckResource(object):
    # This is used to start and check the results of the integrity check operation.
    # on_post: start
    # on_get: status
    pass

class DataResource(object):
    # This is used to store and retrieve the chunks of data.
    _CHUNK_SIZE_BYTES = 4096
    
    def __init__(self, chunk_store):
        self._chunk_store = chunk_store
    
    # on_get: retrieve chunk
    # on_post: store chunk
    def on_post(self, req, resp):
        name = self._chunk_store.save(req.bounded_stream.read())
        resp.status = falcon.HTTP_CREATED
        resp.location = '/data/{}'.format(name)
