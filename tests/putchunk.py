#!/usr/local/bin/python

# postchunk.py
# A quick script to post a test chunk to the storage server.
# Daniel Williams <dwilliams@port8080.net>

### IMPORTS ####################################################################
import requests
import argparse
import hashlib

### GLOBALS ####################################################################

### FUNCTIONS ##################################################################

### MAIN #######################################################################
def main():
    # Parse the command line arguments.
    argparser = argparse.ArgumentParser(description = "A quick script to post a test chunk to the storage server.")
    argparser.add_argument('--host', help = "Storage daemon host address to send to")
    argparser.add_argument('--port', type=int, help = "Storage daemon host port to send to")
    argparser.add_argument('filename', help = "Chunk to send")
    args = argparser.parse_args()

    # Build the URL and request data
    chunk = open(args.filename, 'rb').read()

    mdfive = hashlib.md5(chunk)
    shaone = hashlib.sha1(chunk)

    url = "http://%s:%d/data/%s/%s" % (args.host, args.port, mdfive.hexdigest(), shaone.hexdigest())
    headers = {'Content-Type': 'application/octet-stream'}

    print "MD5:  %s\nSHA1: %s" % (mdfive.hexdigest(), shaone.hexdigest())

    r = requests.put(url, data=chunk, headers=headers)

    print r.text

if __name__ == "__main__":
    main()
