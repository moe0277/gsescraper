'''
Created on Apr 14, 2018

@author: mkhan
'''

from configparser import ConfigParser
from lib.scraper import GSEScraper

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


def main():
    program_name_full = os.path.basename(sys.argv[0])
    program_name = os.path.splitext(program_name_full)[0]
 
    configlogging()
    cfgfile="./%s.ini" % program_name

    parseconfig(cfgfile)
    
    gses = GSEScraper(CONFIG['username'], CONFIG['password'], CONFIG['environments'])   
    print(CONFIG['environments'])
    gses.prep()
    gses.getstatus()
    for env in gses.envs:
        if gses.envhash[env]["status"] == "Completed":
            logging.info("Cleaning env: "+env)
            gses.envclean(env)
        else:
            logging.info("Not cleaning env: "+env)

    print(gses.envhash)

if __name__ == '__main__':
    main()