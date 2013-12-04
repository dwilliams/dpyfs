#!/usr/local/bin/python

# storaged.py
# A python based simple storage daemon for the dpyfs project.
# Daniel Williams <dwilliams@port8080.net>

### IMPORTS ############################################################################################################
import logging
import argparse
import ConfigParser
import hashlib
import web
import os
import platform
import json

if platform.system() == 'Windows':
    import ctypes

### GLOBALS ############################################################################################################
config = None
numChunks = 0

### FUNCTIONS ##########################################################################################################
# View function for the good ol' 404
def notFound():
    return web.notfound("<html><body><h1>404 Not Found</h1>\n"
                        "<p>Somethin's amiss.  Might want to check them URLs again.</p></body></html>")

# View function for a lovely little internal error
def internalError():
    return web.internalerror("<html><body><h1>500 Internal Server Error</h1>\n"
                             "<p>I guess I've lost my tools in my hands again.</p></body></html>")

# Helper function to get free space and total space information (in megabytes)
def diskSpace(path):
    freespace = 0
    freespacenonsuper = 0
    totalspace = 0
    print "diskSpace(%s): platform = %s" % (path, platform.system())
    # If we're on Windows
    if platform.system() == 'Windows':
        freespace = ctypes.c_ulonglong(0)
        freespacenonsuper = ctypes.c_ulonglong(0)
        totalspace = ctypes.c_ulonglong(0)
        # NOTE: totalspace here is the total space available to the user, not total space on the disk.
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(path),
                                                   ctypes.pointer(freespacenonsuper),
                                                   ctypes.pointer(totalspace),
                                                   ctypes.pointer(freespace))
    else:
        # We're on a decent system...
        stat = os.statvfs(path)
        freespace = st.f_bfree * st.f_frsize
        freespacenonsuper = st.f_bavail * st.f_frsize
        totalspace = st.f_blocks * f_frsize
    # return a tuple of the yummy info
    return (freespace.value / (1024 * 1024), freespacenonsuper.value / (1024 * 1024), totalspace.value / (1024 * 1024))

# Helper function to check the chunks in the storageDir and set the counters
def checkChunks(path):
    chunkCounter = 0
    for root, dir, files in os.walk(path):
        logging.debug("checkChunks: root:  %s" % (root))
        logging.debug("checkChunks: dir:   %s" % (str(dir)))
        logging.debug("checkChunks: files: %s" % (str(files)))
        for curfile in files:
            isChunkGood = True
            logging.debug("checkChunks:    curfile: %s" % (curfile))
            # Grab the chunk
            chunk = open(os.path.abspath("%s/%s" % (root, curfile)), 'rb').read()
            # check it's size
            if len(chunk) != config.getBlockSize():
                # The chunk is the wrong size.
                logging.warning("Somebody's touched the file system again.")
                isChunkGood = False
            # hash it
            mdfive = hashlib.md5(chunk).hexdigest()
            shaone = hashlib.sha1(chunk).hexdigest()
            # check the path
            curpath = "%s/" % (config.getStorageDir())
            for i in range(0, len(mdfive), 3):
                curpath += "%s/" % (mdfive[i:i+3])
            if(os.path.abspath(curpath) != os.path.abspath(root)):
                # The chunk hashed badly.
                logging.warning("Somebody's touched the file system again.")
                logging.debug("  root:    %s" % (os.path.abspath(root)))
                logging.debug("  curpath: %s" % (os.path.abspath(curpath)))
                isChunkGood = False
            # check the filename
            if(curfile != ("%s.obj" % (shaone))):
                # The chunk hashed badly.
                logging.warning("Somebody's touched the file system again.")
                logging.debug("  curfile: %s" % (curfile))
                logging.debug("  shaone:  %s" % (shaone))
                isChunkGood = False
            # if it's good, increment counter
            if(isChunkGood):
                chunkCounter += 1
            # if it's bad delete the chunk
            else:
                logging.warning("Cleaning up other's meddling")
                os.remove("%s/%s" % (root, curfile))
    # delete any empty directories (should have function in os module that does this)
    try:
        os.removedirs(path)
    except OSError as ex:
        logging.debug("Failed to remove a directory: %s" % (ex))
    return chunkCounter

### CLASSES ############################################################################################################
# Controller class for redirecting the root to another place
class index:
    def GET(self):
        raise web.seeother('/info')

# Controller class for infomation display pages.
class info:
    def GET(self, parameterString = None):
        global config, numChunks
        path = config.getStorageDir()
        # If /info/integritycheck is called, run the integrity check function.
        if(parameterString == 'integritycheck'):
            numChunks = checkChunks(path)
        info = {'numchunks': numChunks}
        info['spacefree'], info['spacefreenonsuper'], info['spacetotal'] = diskSpace(path)
        logging.debug("SF:   %s\nSFNS: %s\nTS:   %s" % (info['spacefree'], info['spacefreenonsuper'], info['spacetotal']))
        try:
            info['percentfreenonsuper'] = 100 * (float(info['spacefreenonsuper']) / info['spacetotal'])
        except ZeroDivisionError:
            info['percentfreenonsuper'] = 0
        contentType = web.ctx.env.get('HTTP_ACCEPT')
        logging.debug("/info GET Content-Type: %s" % (contentType))
        if(contentType == 'application/json'):
            web.header('Content-Type', 'application/json')
            result = json.dumps(info)
        else:
            web.header('Content-Type', 'text/html')
            result = "<html><body><h1>dpyfs Storage Daemon</h1>\n"
            result += "<h3>Diskspace:</h3>\n"
            result += "Total Space:  %d MB<br />\n" % (info['spacetotal'])
            result += "Free Space:   %d MB<br />\n" % (info['spacefreenonsuper'])
            result += "Percent Free: %d%%<br />\n" % (info['percentfreenonsuper'])
            result += "Number of Chunks: %d<br />" % (info['numchunks'])
        return result

# Controller class for accessing file chunks.
class data:
    def GET(self, hashMD5, hashSHA1):
        global config
        # Build the path and read the file
        path = "%s/" % (config.getStorageDir())
        for i in range(0, len(hashMD5), 3):
            path += "%s/" % (hashMD5[i:i+3])
        path += "%s.obj" % (hashSHA1)
        ## Should try catch around this file read...
        if not os.path.isfile(path):
            logging.info("File not found: %s" % (path))
            return web.notfound()
        chunk = open(path, 'rb').read()
        # Verify the sums
        mdfive = hashlib.md5(chunk).hexdigest()
        shaone = hashlib.sha1(chunk).hexdigest()
        # Return the chunk
        if mdfive == hashMD5 and shaone == hashSHA1:
            web.header("Content-Type", "application/octet-stream")
            return chunk
        # Return an error here
        logging.error("There's a skeleton in my closet! GET - %s" % (path))
        return web.internalerror()

    def PUT(self, hashMD5, hashSHA1):
        global config, numChunks
        # Make sure we're getting the right content-type
        contentType = web.ctx.env.get('CONTENT-TYPE')
        if(contentType != 'application/octet-stream'):
            # Not an octet stream, log a warning.  We'll still store the chunk if it passes everything else.
            logging.warning("Somebody's giving me something I don't like.")
            logging.debug("PUT Content-Type: %s" % (contentType))
        # Grab the chunk and calc the sums
        chunk = web.data()
        if len(chunk) != config.getBlockSize():
            # The chunk is wrong.  Return a 400 bad request error. Log info about the remote in the future.
            logging.warning("Somebody's passing around a bad brownie.")
            logging.debug("actual chunk size: %d" % (len(chunk)))
            logging.debug("config chunk size: %d" % (config.getBlockSize()))
            return web.badrequest()
        mdfive = hashlib.md5(chunk).hexdigest()
        shaone = hashlib.sha1(chunk).hexdigest()
        # Build the path and write the file
        path = "%s/" % (config.getStorageDir())
        for i in range(0, len(mdfive), 3):
            path += "%s/" % (mdfive[i:i+3])
        if not os.path.exists(path):
            # I've read that this isn't the best way to do this, but I can
            # always make it better later...
            os.makedirs(path)
        path += "%s.obj" % (shaone)
        ## At this point I should see if the file exists.  If it does, verify
        ## checksums, otherwise write the file and then verify the checksums
        if not os.path.isfile(path):
            # Write the file
            logging.debug("Adding new chunk at: %s" % (path))
            writeResult = open(path, 'wb').write(chunk)
        # Read the file back and verify the sums
        verifyChunk = open(path, 'rb').read()
        verifyMdfive = hashlib.md5(verifyChunk).hexdigest()
        verifyShaone = hashlib.sha1(verifyChunk).hexdigest()
        # If the sums match, return a 200 OK (return the sums for now)
        # otherwise return a 500 error (we have a file that doesn't match)
        if verifyMdfive == mdfive or verifyShaone == shaone:
            numChunks += 1
            return "Success"
        # Return an error here
        logging.error("There's a skeleton in my closet! PUT - %s" % (path))
        return web.internalerror()

    def DELETE(self, hashMD5, hashSHA1):
        global config, numChunks
        # Build the path and read the file
        path = "%s/" % (config.getStorageDir())
        for i in range(0, len(hashMD5), 3):
            path += "%s/" % (hashMD5[i:i+3])
        path += "%s.obj" % (hashSHA1)
        ## Should try catch around this file read...
        if not os.path.isfile(path):
            logging.info("File not found: %s" % (path))
            return web.notfound()
        chunk = open(path, 'rb').read()
        # Verify the sums
        mdfive = hashlib.md5(chunk).hexdigest()
        shaone = hashlib.sha1(chunk).hexdigest()
        # Delete the file.  I'll leave deleting the directories for a cleanup
        # task that'll be run by cron.
        if mdfive == hashMD5 and shaone == hashSHA1:
            os.remove(path)
            numChunks -= 1
            return "Success"
        # Return an error here
        logging.error("There's a skeleton in my closet! DELETE - %s" % (path))
        return web.internalerror()

    # Do I need to implement this ass an error, or just leave it out?
    #def POST(self, hashMD5, hashSHA1):
    #    return "Not yet implemented.  May not implement in the future."

# Config handling class.  This should never be accessed by the clients directly.
class dpyfsConfig:
    configFile = '/etc/dpyfs/storaged.conf'
    configSection = 'storage'
    # Config file entries always come back lower case.
    ipaddr = '0.0.0.0'
    port = '8080'
    storagedir = '/var/dpyfs/data'
    blocksize = '8'

    # Initialize the configuration class
    def __init__(self, conFile = None):
        if conFile is not None:
            self.configFile = conFile
        # Load the config from the file
        self.tmpConfig = ConfigParser.ConfigParser()
        self.tmpConfig.read(self.configFile)

    # Load the config from the proper section
    def load(self, section = None):
        if section is not None:
            self.configSection = section
        # Read the config options from the section. Need a try catch with better
        # error handling here.
        logging.debug("Read from config file:")
        for key, value in self.tmpConfig.items(self.configSection):
            setattr(self, key, value)
            logging.debug("  %s = %s" % (key, value))

    # Create an IP address for the webserver to use
    def getIP(self):
        return web.net.validip("%s:%s" % (self.ipaddr, self.port))

    # Grab the blockSize and convert to bytes from kilobytes
    def getBlockSize(self):
        return int(self.blocksize) * 1024

    # Grab the storage directory (make absolute path if needed)
    def getStorageDir(self):
        # FIXME: Make this convert to absolute path if necessary
        return os.path.abspath(self.storagedir)

### MAIN ###############################################################################################################
def main():
    global config, numChunks

    # Turn on verbose logging.  I'll make this config driven at a future date.
    logging.basicConfig(level=logging.DEBUG)

    # Parse the command line arguments.
    argparser = argparse.ArgumentParser(description = "The storage daemon for the dpyfs project.")
    argparser.add_argument('--configFile', help = "Configuration file to read from")
    argparser.add_argument('--configSection', help = "Section in the configuration file to use")
    args = argparser.parse_args()
    logging.debug('Argument datastructure: \n    %s' % (str(args)))

    # Parse the config file.
    if args.configFile is not None:
        config = dpyfsConfig(args.configFile)
    else:
        config = dpyfsConfig()

    if args.configSection is not None:
        config.load(args.configSection)
    else:
        config.load()

    # Setup the webserver for handling requests.
    urls = ('/', 'index',
            '/data/([0-9,a-f,A-F]+)/([0-9,a-f,A-F]+)', 'data',
            '/info', 'info',
            '/info/(.*)', 'info')

    app = web.application(urls, globals())
    app.notfound = notFound
    app.internalerror = internalError
    # Check chunks if there are any in the storage directory
    numChunks = checkChunks(config.getStorageDir())
    # Run the webserver
    web.httpserver.runsimple(app.wsgifunc(), config.getIP())

if __name__ == "__main__":
    main()
