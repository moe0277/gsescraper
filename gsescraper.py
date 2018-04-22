'''
Created on Apr 14, 2018

@author: moe0277
@contact: moe.f.khan@oracle.com
@copyright: Copyright (C) Oracle Corporation

gsescraper automates password scraping, cleaning, and password resetting of owned GSE environments.

Pre-requisites:

python modules:
    1. xlsxwriter
    2. splinter
    
For more information, see README.md
'''

from configparser  import ConfigParser
from lib.scraper   import GSEScraper

import logging
import sys
import os

CONFIG={} # holds config file information

def configLogging(logfile):
    """
    Setup console and file logging
    console level: debug
    file lelvel: info
    """
    logging.basicConfig(filename=logfile, level=logging.INFO, format="[%(asctime)s] %(levelname)-8s %(message)s", datefmt='%H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    logging.info('Starting..')

def parseConfig(cfgfile):
    """
    Populate the CONFIG variable with .ini content
    """
    config = ConfigParser()
    config.read(cfgfile)
    CONFIG['username'] = config.get("common", "username")
    CONFIG['password'] = config.get("common", "password")
    CONFIG['environments'] = tuple(config.get("common", "environments").split(","))
    CONFIG['mode'] = config.get("common", "mode")
    logging.info('Config file parsed: %s' % str(CONFIG))

def main():
    program_name_full = os.path.basename(sys.argv[0])
    program_name = os.path.splitext(program_name_full)[0]
 
    configLogging(program_name + ".log")
    cfgfile="./%s.ini" % program_name

    parseConfig(cfgfile)
    
    gses = GSEScraper(CONFIG['username'], CONFIG['password'], CONFIG['environments'])   
    gses.prep()
    logging.info("Prep complete")
    
    if CONFIG['mode'] == 'status':
        logging.info("Mode: status")
        gses.getStatus()
        logging.info("Environments status:")
        for k, v in gses.envs.items():
            logging.debug(v)        
        logging.info("Writing xls")   
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