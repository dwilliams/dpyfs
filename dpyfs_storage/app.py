#!/usr/bin/env python3

### IMPORTS ###
import os
import falcon

### GLOBALS ###
BLOCK_SIZE_BYTES = 64 * 1024 # 64K
STORAGE_DIR = os.path.abspath("./data/") # Fix these later
CONFIG_DIR = os.path.abspath("./etc/dpyfs/") # Fix these later

### FUNCTIONS ###

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
    # on_post: store chunk
    # on_get: retrieve chunk
    pass

### MAIN ###
app = application = falcon.API()

app.add_route('/', RootResource())
