'''
Created on Apr 14, 2018

@author: moe0277
@contact: moe.f.khan@oracle.com
'''

from configparser  import ConfigParser
from lib.scraper   import GSEScraper

import logging
import sys
import os

CONFIG={}

def configlogging():
    logging.basicConfig(filename="%s.log" % os.path.basename(sys.argv[0]), level=logging.DEBUG, format="[%(asctime)s] %(levelname)-8s %(message)s", datefmt='%H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    logging.debug('Starting..')

def parseconfig(cfgfile):
    config = ConfigParser()
    config.read(cfgfile)
    CONFIG['username'] = config.get("common", "username")
    CONFIG['password'] = config.get("common", "password")
    CONFIG['environments'] = tuple(config.get("common", "environments").split(","))
    CONFIG['mode'] = config.get("common", "mode")

def main():
    program_name_full = os.path.basename(sys.argv[0])
    program_name = os.path.splitext(program_name_full)[0]
 
    configlogging()
    cfgfile="./%s.ini" % program_name

    parseconfig(cfgfile)
    
    gses = GSEScraper(CONFIG['username'], CONFIG['password'], CONFIG['environments'])   
    gses.prep()
    
    if CONFIG['mode'] == 'status':
        logging.info("Mode: status")
        gses.getStatus()
        logging.debug("Environments status:")
        for k, v in gses.envs.items():
            logging.debug(v)        
        logging.debug("Writing xls")   
        gses.writeXls('gsescraper.xlsx')
    elif CONFIG['mode'] == "clean":
        logging.info("Mode: clean")
        gses.envClean()    
    elif CONFIG['mode'] == "passwordreset":
        logging.info("Mode: passwordreset")
        gses.envPass()
    
    if CONFIG['mode'] != "status":
        success = []
        others = []
        for k, v in gses.envs.items():
            if v.modestatus:
                success.append(k)
            else:
                others.append(k)
        logging.info("Ran %s on: %s" % (CONFIG['mode'], str(success)))
        logging.info("Skipped: %s" % str(others))
        
if __name__ == '__main__':
    main()