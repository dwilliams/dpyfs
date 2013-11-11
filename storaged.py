#!/usr/local/bin/python

# storaged.py
# A python based simple storage daemon for the dpyfs project.
# Daniel Williams <dwilliams@port8080.net>

### IMPORTS ####################################################################
import argparse
import ConfigParser
import hashlib
import web

### GLOBALS ####################################################################
config = ConfigParser.ConfigParser()
configSection = ''

### FUNCTIONS ##################################################################

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

### MAIN #######################################################################
def main():
    # Parse the command line arguments.
    argparser = argparse.ArgumentParser(description = "The storage daemon for the dpyfs project.")
    argparser.add_argument('--configFile', help = "Configuration file to read from")
    argparser.add_argument('--configSection', help = "Section in the configuration file to use")
    args = argparser.parse_args()
    
    # Parse the config file.
    if 'configFile' in args:
        config.read(args.configFile)
    else:
        config.read('/etc/dpyfs/storaged.conf')
    
    if 'configSection' in args:
        configSection = args.configSection
    else:
        configSection = 'storage'
    
    ## Setup the configuration class here.
    
    # Setup the webserver for handling requests.
    urls = ('/', 'index',
            '/data/([0-9,a-f,A-F]+)/([0-9,a-f,A-F]+)', 'data',
            '/info', 'info')
    
    app = web.application(urls, globals())
    # Should update this to use web.net.validip()
    web.httpserver.runsimple(app.wsgifunc(), ("0.0.0.0", config.getint(configSection, 'port')))

if __name__ == "__main__":
    main()
