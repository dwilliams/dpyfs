#!/usr/bin/env python3

### IMPORTS ###
import os

import hashlib
import requests

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class ChunkingObjectStore(object):
    def __init__(self, chunk_max_bytes=65536):
        self._chunk_max_bytes = chunk_max_bytes

    def save(self, object_data_stream):
        # Grab chunk of _chunk_max_bytes size
        # Calculate hashes of chunk
        # Store chunk on STORAGE_DUPLICATION_FACTOR number of storage servers
        # Record chunk metadata
        # Repeat until no data
        # Return the path of the object
        pass

    def open(self):
        return None # Should return a stream object for the webserver to stream back to the client
