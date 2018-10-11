#!/usr/bin/env python3

### IMPORTS ###
import hashlib
import io
import os
import pytest

from unittest.mock import MagicMock, mock_open, call

from dpyfs.chunk_stores import FilesystemChunkStore

### GLOBALS ###
CHUNK_SIZE = 65536
MOCK_STORAGE_PATH = "/tmp/data/"

### FUNCTIONS ###
def random_chunk():
    return os.urandom(CHUNK_SIZE) # 64K

def random_large_chunk():
    return os.urandom(CHUNK_SIZE + ord(os.urandom(1))) # 64K

# Normal, full length byte strings that may screw something up.
@pytest.fixture(params=[random_chunk() for i in range(3)])
def normal_chunk(request):
    return request.param

# Odd ball byte strings that may screw something up.
@pytest.fixture(
    params=[
        b'\0', # Null Byte
        b'', # Empty String
        b'1234', # Short String
    ])
def odd_chunk(request):
    return request.param

# Too large byte strings that may screw something up.
@pytest.fixture(params=[random_large_chunk() for i in range(3)])
def large_chunk(request):
    return request.param

### CLASSES ###
class TestFilesystemChunkStore(object):
    # Normal, full chunks
    def test_get_chunk_path(self, normal_chunk):
        tmp_sha512_digest = hashlib.sha512(normal_chunk).hexdigest()
        tmp_md5_digest = hashlib.md5(normal_chunk).hexdigest()

        dut = FilesystemChunkStore(MOCK_STORAGE_PATH, CHUNK_SIZE, mock_open())

        tmp_chunk_path = "{}{}/{}-{}.chunk".format(MOCK_STORAGE_PATH, tmp_md5_digest[0:4], tmp_md5_digest, tmp_sha512_digest)
        dut_chunk_path = dut._get_chunk_path(tmp_sha512_digest, tmp_md5_digest)

        assert dut_chunk_path == tmp_chunk_path

    def test_save(self, normal_chunk):
        tmp_sha512_digest = hashlib.sha512(normal_chunk).hexdigest()
        tmp_md5_digest = hashlib.md5(normal_chunk).hexdigest()

        mock_file_open = mock_open()
        dut = FilesystemChunkStore(MOCK_STORAGE_PATH, CHUNK_SIZE, mock_file_open)

        dut_sha512_digest, dut_md5_digest = dut.save(normal_chunk)

        assert dut_sha512_digest == tmp_sha512_digest
        assert dut_md5_digest == tmp_md5_digest

        # Need to add filesystem mock to check the file contents.
        assert call().write(normal_chunk) in mock_file_open.mock_calls
        # This works for now, but should really move to "one of the in-memory filesystem packages on PyPI"

    def test_open(self, normal_chunk):
        tmp_sha512_digest = hashlib.sha512(normal_chunk).hexdigest()
        tmp_md5_digest = hashlib.md5(normal_chunk).hexdigest()

        mock_file_open = mock_open(read_data = normal_chunk)
        dut = FilesystemChunkStore(MOCK_STORAGE_PATH, CHUNK_SIZE, mock_file_open)

        dut_chunk_data = dut.open(tmp_sha512_digest, tmp_md5_digest)

        assert dut_chunk_data == normal_chunk
        # This works for now, but should really move to "one of the in-memory filesystem packages on PyPI"

    # Odd ball chunks
    def test_odd_get_chunk_path(self, odd_chunk):
        pass
    
    def test_odd_save(self, odd_chunk):
        pass
    
    def test_odd_open(self, odd_chunk):
        pass

    # Too large of chunks
    def test_large_get_chunk_path(self, large_chunk):
        pass
    
    def test_large_save(self, large_chunk):
        pass
    
    def test_large_open(self, large_chunk):
        pass
