#!/usr/bin/env python3

### IMPORTS ###
import hashlib
import io
import os
import unittest

from pyfakefs import fake_filesystem_unittest

from dpyfs.chunk_stores.filesystem import ChunkStore

### GLOBALS ###
CHUNK_SIZE = 65536
MOCK_STORAGE_PATH = "/tmp/data/"

### FUNCTIONS ###

### CLASSES ###
class TestChunkStore(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    # Normal, but using a fake filesystem instead of method mocks
    def test_save(self):
        normal_chunk = os.urandom(CHUNK_SIZE)
        tmp_sha512_digest = hashlib.sha512(normal_chunk).hexdigest()
        tmp_md5_digest = hashlib.md5(normal_chunk).hexdigest()

        tmp_chunk_path = "{}{}/{}-{}.chunk".format(MOCK_STORAGE_PATH, tmp_md5_digest[0:4], tmp_md5_digest, tmp_sha512_digest)

        dut = ChunkStore(MOCK_STORAGE_PATH, CHUNK_SIZE, io.open)

        dut_sha512_digest, dut_md5_digest = dut.save(normal_chunk)

        assert dut_sha512_digest == tmp_sha512_digest
        assert dut_md5_digest == tmp_md5_digest

        with open(tmp_chunk_path, 'rb') as tmp_file:
            tmp_contents = tmp_file.read()

        assert tmp_contents == normal_chunk

    def test_open(self):
        normal_chunk = os.urandom(CHUNK_SIZE)
        tmp_sha512_digest = hashlib.sha512(normal_chunk).hexdigest()
        tmp_md5_digest = hashlib.md5(normal_chunk).hexdigest()

        tmp_chunk_path = "{}{}/{}-{}.chunk".format(MOCK_STORAGE_PATH, tmp_md5_digest[0:4], tmp_md5_digest, tmp_sha512_digest)
        self.fs.create_file(tmp_chunk_path, contents=normal_chunk)
        self.assertTrue(os.path.exists(tmp_chunk_path))

        dut = ChunkStore(MOCK_STORAGE_PATH, CHUNK_SIZE, io.open) # Have to pass io.open post patching.

        dut_chunk_data = dut.open(tmp_sha512_digest, tmp_md5_digest)

        assert dut_chunk_data == normal_chunk