#!/usr/bin/env python3

### IMPORTS ###
import falcon
import pytest

from falcon import testing

from dpyfs_storage.app import app

### GLOBALS ###

### FUNCTIONS ###
@pytest.fixture
def client():
    return testing.TestClient(app)

def test_root(client):
    expect_str = "Hello dpyfs!"
    
    response = client.simulate_get('/')
    result_str = response.content.decode('utf-8')
    
    assert result_str == expect_str
    assert response.status == falcon.HTTP_OK

### CLASSES ###
