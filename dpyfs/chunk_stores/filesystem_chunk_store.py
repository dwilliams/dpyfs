#!/usr/bin/env python3

### IMPORTS ###
import io
import os
import hashlib

### GLOBALS ###

### FUNCTIONS ###

### CLASSES ###
class FilesystemChunkStore(object):
    def __init__(self, storage_path, chunk_max_bytes=65536, fopen=io.open):
        self._storage_path = storage_path
        self._chunk_max_bytes = chunk_max_bytes
        self._fopen = fopen

    def _get_chunk_path(self, sha512_hex, md5_hex):
        # should regex check the hashes to make sure they're {0-9a-f}
        if not len(sha512_hex) == 128 or not len(md5_hex) == 32:
            raise Exception("Bad hash")
        return os.path.join(self._storage_path, md5_hex[0:4], "{}-{}.chunk".format(md5_hex, sha512_hex))

    def save(self, chunk_data):
        if not isinstance(chunk_data, bytes):
            raise Exception("Not a data chunk.  Must be bytes-like object.")

        if len(chunk_data) > self._chunk_max_bytes:
            raise Exception("Chunk too large")

        sha512_digest = hashlib.sha512(chunk_data).hexdigest()
        md5_digest = hashlib.md5(chunk_data).hexdigest()
        
        chunk_path = self._get_chunk_path(sha512_digest, md5_digest)

        # Add possible compression here

        if not os.path.exists(os.path.dirname(chunk_path)):
            os.makedirs(os.path.dirname(chunk_path))

        with self._fopen(chunk_path, 'wb') as chunk_file:
            chunk_file.write(chunk_data)

        return (sha512_digest, md5_digest)

    def open(self, sha512_digest, md5_digest):
        chunk_path = self._get_chunk_path(sha512_digest, md5_digest)

        with self._fopen(chunk_path, 'rb') as chunk_file:
            chunk_data = chunk_file.read()

        # Add possible decompression here

        if len(chunk_data) > self._chunk_max_bytes:
            raise Exception("Chunk invalid")

        return chunk_data
