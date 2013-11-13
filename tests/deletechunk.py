#!/usr/local/bin/python

# deletechunk.py
# A quick script to delete a test chunk from the storage server.
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
    argparser = argparse.ArgumentParser(description = "A quick script to delete a test chunk from the storage server.")
    argparser.add_argument('--host', help = "Storage daemon host address to send to")
    argparser.add_argument('--port', type=int, help = "Storage daemon host port to send to")
    argparser.add_argument('md5', help = "Chunk to send")
    argparser.add_argument('sha1', help = "Chunk to send")
    args = argparser.parse_args()
    
    # Build the URL and request data
    url = "http://%s:%d/data/%s/%s" % (args.host, args.port, args.md5, args.sha1)
    print "Requested sums:"
    print "  MD5:  %s\n  SHA1: %s" % (args.md5, args.sha1)
    
    r = requests.delete(url)
    
    print "Result: %s" % (r.text)

if __name__ == "__main__":
    main()
