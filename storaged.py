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

### GLOBALS ####################################################################

### FUNCTIONS ##################################################################
# View function for the good ol' 404
def notFound():
    return web.notfound("404 Not Found\n"
                        "Somethin's amiss.  Might want to check them URLs again.")

# View function for a little internal error love
def internalError():
    return web.internalerror("500 Internal Server Error\n"
                             "I guess I've lost my tools in my hands again.")

### CLASSES ####################################################################
# Controller class for redirecting the root to another place
class index:
    def GET(self):
        raise web.seeother('/info')

# Controller class for infomation display pages.
class info:
    def GET(self):
        return "Hello World"

# Controller class for accessing file chunks.
class data:
    def GET(self, hashMD5, hashSHA1):
        return "No data here currently."

    def PUT(self, hashMD5, hashSHA1):
        return "Not yet implemented.  Coming soon!"

    def DELETE(self, hashMD5, hashSHA1):
        return "Not yet implemented.  Coming soon!"

    # Do I need to implement this ass an error, or just leave it out?
    def POST(self, hashMD5, hashSHA1):
        return "Not yet implemented.  May not implement in the future."

# Config handling class.  This should never be accessed by the clients directly.
class dpyfsConfig:
    configFile = '/etc/dpyfs/storaged.conf'
    configSection = 'storage'
    ipaddr = '0.0.0.0'
    port = 8080
    storageDir = '/var/dpyfs/data'

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
        for key, value in self.tmpConfig.items(self.configSection):
            setattr(self, key, value)

    # Create an IP address for the webserver to use
    def getIP(self):
        return web.net.validip("%s:%d" % (self.ipaddr, self.port))

### MAIN #######################################################################
def main():
    # Turn on verbose logging.  I'll make this config driven at a future date.
    logging.basicConfig(level=logging.DEBUG)

    # Parse the command line arguments.
    argparser = argparse.ArgumentParser(description = "The storage daemon for the dpyfs project.")
    argparser.add_argument('--configFile', help = "Configuration file to read from")
    argparser.add_argument('--configSection', help = "Section in the configuration file to use")
    args = argparser.parse_args()
    logging.debug('Argument datastructure: \n%s' % (str(args)))

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
