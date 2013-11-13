#!/usr/local/bin/python

# storaged.py
# A python based simple storage daemon for the dpyfs project.
# Daniel Williams <dwilliams@port8080.net>

### IMPORTS ####################################################################
import logging
import argparse
import ConfigParser
import hashlib
import web
import os
import platform

if platform.system() == 'Windows':
    import ctypes

### GLOBALS ####################################################################
config = None

### FUNCTIONS ##################################################################
# View function for the good ol' 404
def notFound():
    return web.notfound("<html><body><h1>404 Not Found</h1>\n"
                        "<p>Somethin's amiss.  Might want to check them URLs again.</p></body></html>")

# View function for a lovely little internal error
def internalError():
    return web.internalerror("<html><body><h1>500 Internal Server Error</h1>\n"
                             "<p>I guess I've lost my tools in my hands again.</p></body></html>")

# Helper function to get free space and total space information
def diskSpace(path):
    freespace = 0
    freespacenonsuper = 0
    totalspace = 0
    # If we're on Windows
    if platform.system() == 'Windows':
        freespace = ctypes.c_ulonglong(0)
        freespacenonsuper = ctypes.c_ulonglong(0)
        totalspace = ctypes.c_ulonglong(0)
        # NOTE: totalspace here is the total space available to the user, not
        #       total space on the disk.
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
    return (freespace.value, freespacenonsuper.value, totalspace.value)

### CLASSES ####################################################################
# Controller class for redirecting the root to another place
class index:
    def GET(self):
        raise web.seeother('/info')

# Controller class for infomation display pages.
class info:
    def GET(self):
        global config
        path = "%s/" % (config.getStorageDir())
        spacefree, spacefreenonsuper, spacetotal = diskSpace(path)
        print "SF:   %s\nSFNS: %s\nTS:   %s" % (spacefree, spacefreenonsuper, spacetotal)
        try:
            percentfree = 100 * (float(spacefree) / spacetotal)
        except ZeroDivisionError:
            percentfree = 0
        try:
            percentused = 100 * (float(spacetotal - spacefree) / spacetotal)
        except ZeroDivisionError:
            percentfree = 0
        try:
            percentfreenonsuper = 100 * (float(spacefreenonsuper) / spacetotal)
        except ZeroDivisionError:
            percentfree = 0
        result = "<html><body><h1>dpyfs Storage Daemon</h1>\n"
        result += "<h3>Diskspace:</h3>\n"
        result += "Total Size:   %d<br />\n" % (spacetotal)
        result += "Free Size:    %d<br />\n" % (spacefree)
        result += "Free Size:    %d (non-superuser)<br />\n" % (spacefreenonsuper)
        result += "Percent Free: %d<br />\n" % (percentfree)
        result += "Percent Free: %d (non-superuser)<br />\n" % (percentfreenonsuper)
        result += "Percent Used: %d<br />\n" % (percentused)
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
        global config
        # Grab the chunk and calc the sums
        ## Do I want to check the Content-Type for application/octet-stream here?
        chunk = web.data()
        if len(chunk) != config.getBlockSize():
            # The chunk is wrong.  Return a 400 bad request error. Log info
            # about the remote in the future.
            logging.warning("Somebody's passing around a bad brownie.")
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
            return "Success"
        # Return an error here
        logging.error("There's a skeleton in my closet! PUT - %s" % (path))
        return web.internalerror()

    def DELETE(self, hashMD5, hashSHA1):
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
        # Delete the file.  I'll leave deleting the directories for a cleanup
        # task that'll be run by cron.
        if mdfive == hashMD5 and shaone == hashSHA1:
            os.remove(path)
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
        return self.storagedir

### MAIN #######################################################################
def main():
    global config

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
            '/info', 'info')

    app = web.application(urls, globals())
    app.notfound = notFound
    app.internalerror = internalError
    # Should update this to use web.net.validip()
    web.httpserver.runsimple(app.wsgifunc(), config.getIP())

if __name__ == "__main__":
    main()
