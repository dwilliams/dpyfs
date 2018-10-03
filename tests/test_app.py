#!/usr/bin/env python3

### IMPORTS ###
import io
import pytest

import falcon

from falcon import testing
from unittest.mock import mock_open, call, MagicMock

import dpyfs_storage.app

### GLOBALS ###

### FUNCTIONS ###
@pytest.fixture
def mock_store():
    return MagicMock()

@pytest.fixture
def client(mock_store):
    app = dpyfs_storage.app.create_app(mock_store)
    return testing.TestClient(app)

def test_root(client):
    expect_str = "Hello dpyfs!"
    
    response = client.simulate_get('/')
    result_str = response.content.decode('utf-8')
    
    assert result_str == expect_str
    assert response.status == falcon.HTTP_OK

# With clever composition of fixtures, we can observe what happens with
# the mock injected into the image resource.
def test_post_data_chunk(client, mock_store):
    # file_name = 'fake_image_name.xyz'
    # 
    # # We need to know what ImageStore method will be used
    # mock_store.save.return_value = file_name
    # 
    # response = client.simulate_post('/data/', body=b'some-fake-bytes')
    # 
    # assert response.status == falcon.HTTP_CREATED
    # assert response.headers['location'] == '/data/{}'.format(file_name)
    # saver_call = mock_store.save.call_args
# 
    # # saver_call is a unittest.mock.call tuple. It's first element is a
    # # tuple of positional arguments supplied when calling the mock.
    # assert isinstance(saver_call[0][0], falcon.request_helpers.BoundedStream)
    # #assert saver_call[0][1] == image_content_type
    pass

def test_saving_image(monkeypatch):
    # # This still has some mocks, but they are more localized and do not
    # # have to be monkey-patched into standard library modules (always a
    # # risky business).
    # mock_file_open = mock_open()
# 
    # fake_uuid = '123e4567-e89b-12d3-a456-426655440000'
    # def mock_uuidgen():
        # return fake_uuid
# 
    # fake_image_bytes = b'fake-image-bytes'
    # fake_request_stream = io.BytesIO(fake_image_bytes)
    # storage_path = 'fake-storage-path'
    # store = dpyfs_storage.app.ChunkStore(
        # storage_path,
        # uuidgen=mock_uuidgen,
        # fopen=mock_file_open
    # )
# 
    # assert store.save(fake_request_stream) == fake_uuid
    # assert call().write(fake_image_bytes) in mock_file_open.mock_calls
    pass

### CLASSES ###
