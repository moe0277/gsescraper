'''
Created on Apr 3, 2018

@author: moe0277
@copyright: Copyright (C) Oracle Corporation

'''
import time
import logging
import splinter
import re
from lib.xlsmodule import XLSModule

class Environment(object):
    
    def __init__(self, name):
        self.name = name        # name of this environment
        self.password = ""      # password of this environment
        self.status = ""        # status of this environment
        self.recipe = ""        # last recipe
        self.recipelink = ""    # recipe link for this environment
        self.esd = ""           # start time of last recipe
        self.execet = ""        # estimated execution time of last recipe
        self.execaet = ""       # actual execution time of last recipe
        self.owner1 = ""        # primary owner
        self.owner2 = ""        # secondary owner
        self.modestatus = ""    # launched mode 
        
    def __str__(self):
        mString = ""
        mString += self.name + ", "
        mString += self.password + ", "
        mString += self.owner1 + ", "
        mString += self.owner2 + ", "
        mString += self.recipe + ", "
        mString += self.status + ", "
        mString += self.recipelink + ", "
        mString += self.esd + ", "
        mString += self.execet + ", "
        mString += self.execaet
        return mString
        
class GSEScraper(object):
    '''
    classdocs
    '''

    __URL__ = "https://demo.oracle.com/" 

    def __init__(self, username, password, envlist):
        '''
        Constructor
        '''
        self.username = username
        self.password = password
        self.envlist  = envlist
        logging.debug("Processing: "+str(self.envlist))
        
        self.envs = {}
        
        Browser = splinter.Browser
        self.browser = Browser()
                
        logging.debug("Initialized scraper...")
    
    def __login(self):
        if self.browser.is_element_present_by_id('sso_username', 60):
            iUsername = self.browser.find_by_id('sso_username')
        else:
            logging.error("cannot find element: sso_username")
            raise
        if self.browser.is_element_present_by_id('ssopassword', 60):
            iPassword = self.browser.find_by_id('ssopassword')
        else:
            logging.error("cannot find element: ssopassword")
            raise
        if self.browser.is_element_present_by_xpath('/html/body/div/div[3]/div[1]/form/div[2]/span/input', 60):
            iSubmit = self.browser.find_by_xpath('/html/body/div/div[3]/div[1]/form/div[2]/span/input')    
        else:
            logging.error("cannot find element: xpath: /html/body/div/div[3]/div[1]/form/div[2]/span/input")
            raise
        
        logging.debug("Entering username")
        iUsername.fill(self.username)
        
        logging.debug("Entering password")
        iPassword.fill(self.password)

        logging.debug("Submitting")
        iSubmit.click()
    
    def __getEnvLink(self):
        environments = []
        if self.browser.is_element_present_by_xpath('//*[@id="environments"]', 60):
            environments = self.browser.find_by_xpath('//*[@id="environments"]')
            env = environments[0]
            envhtml = env.outer_html
            p = re.compile('href=\"(.*)\"\s*id=')
            g = p.search(envhtml)
            self.envlink = g.group(1)
            logging.info("Envlink: "+self.envlink)
            self.browser.visit(self.__URL__ + self.envlink)
        else:
            logging.error("cannot find element: xpath: '//*[@id=\"environments\"]'")
            raise
        
    def __getEnvBaseLink(self):
        environments = []
        if self.browser.is_element_present_by_xpath("/html/body/form/div/div/table/tbody/tr/td[1]/section/div[2]/div/table/tbody[3]/tr/td/table/tbody/tr/td[4]/a", 60): #the next link i.e. pagination
            environments = self.browser.find_link_by_partial_text("ucm-gse")
            env = environments[0]
            envhtml = env.outer_html
            p = re.compile('href=\"(.*)\"\s*title=')
            g = p.search(envhtml)
            envbaseraw = '/apex/' + g.group(1)
            envbases = envbaseraw.split(":")
            s = ":"
            self.envbaselink = s.join(envbases[:-1])
            logging.info("EnvBaseLik: "+self.envbaselink)
        else:
            logging.error("cannot find element: %s" % "/html/body/form/div/div/table/tbody/tr/td[1]/section/div[2]/div/table/tbody[3]/tr/td/table/tbody/tr/td[4]/a")
            raise
    
    def __visitEnvPage(self, envobj):
        logging.debug("Visiting Env: %s" % envobj.name)
        self.browser.visit(self.__URL__ + self.envbaselink + ":" +envobj.name)
        
    def __getEnvStatus(self, envobj):
        if self.browser.is_element_present_by_id("P15_RECIPE_DISPLAY", 60):
            envrecipe = self.browser.find_by_id("P15_RECIPE_DISPLAY")
            envobj.recipe = envrecipe.text
        if self.browser.is_element_present_by_id("P15_RECIPE_STATUS", 60):
            envstatus = self.browser.find_by_id("P15_RECIPE_STATUS")
            if "Failed" in envstatus.value:
                envstatusval = "Failed"
            elif "Running" in envstatus.value:
                envstatusval = "Running"
            elif "Requested" in envstatus.value:
                envstatusval = "Requested"
            else:
                envstatusval = envstatus.value 
            envobj.status = envstatusval
            
    def __getEnvPass(self, envobj):
        if self.browser.is_element_present_by_id("P15_ENVIRONMENT_AAI_PASSWORD", 60):
            envpass = self.browser.find_by_id("P15_ENVIRONMENT_AAI_PASSWORD")
            envobj.password = envpass.text
            logging.debug("Pass: %s" % envpass.text)
        else:
            logging.error("cannot find element: \"P15_ENVIRONMENT_AAI_PASSWORD\"")
            raise
        return envobj
    
    def __getExecStatus(self, envobj):
        if self.browser.is_element_present_by_id("P15_RECIPE_EXEC_ST_DISPLAY", 60):
            esd = self.browser.find_by_id("P15_RECIPE_EXEC_ST_DISPLAY")
            envobj.esd = esd.text
        else:
            logging.error("cannot find element: \"P15_RECIPE_EXEC_ST_DISPLAY\"")
            raise
        if self.browser.is_element_present_by_id("P15_RECIPE_EXEC_ET_DISPLAY", 60):
            execet = self.browser.find_by_id("P15_RECIPE_EXEC_ET_DISPLAY")
            envobj.execet = execet.text
        else:
            logging.error("cannot find element: \"P15_RECIPE_EXEC_ET_DISPLAY\"")
            raise
        if self.browser.is_element_present_by_id("P15_RECIPE_EXEC_A_ET_DISPLAY",60):
            execaet = self.browser.find_by_id("P15_RECIPE_EXEC_A_ET_DISPLAY")
            envobj.execaet = execaet.text
        else:
            logging.error("cannot find element: \"P15_RECIPE_EXEC_A_ET_DISPLAY\"")
            raise
     
    def __getOwners(self, envobj): 
        if self.browser.is_element_present_by_id("P15_PRIMARY_OWNER", 60):
            owner1 = self.browser.find_by_id("P15_PRIMARY_OWNER")
            envobj.owner1 = owner1.text
        if self.browser.is_element_present_by_id("P15_SECONDARY_OWNER", 60):
            owner2 = self.browser.find_by_id("P15_SECONDARY_OWNER")
            envobj.owner2 = owner2.text
        else:
            logging.error("cannot find element: \"P15_RECIPE_EXEC_ST_DISPLAY\"")
            raise

    def __getRecipeLink(self, envobj):
        logging.info("getRecipeLink entered...")
        if self.browser.is_element_present_by_text("Run DataSet Recipe", 60):
            if self.browser.is_element_present_by_id("pInstance", 60):
                pInstance = self.browser.find_by_id("pInstance")[0].value
                P15_ID = self.browser.find_by_id("P15_INSTANCE_ID")[0].value
                logging.info("pInstance: %s, P15_ID: %s" % (pInstance, P15_ID))
                recipelink = self.envlink[:-2]+":104:"+pInstance+"::NO:104:P104_ENVIRONMENT_ID:"+P15_ID
            #recipeurl = self.browser.find_by_text("Run DataSet Recipe")
            #recipeurlhtml = recipeurl.outer_html
            #p = re.compile('href=\"(.*)\"\s*>')
            #g = p.search(recipeurlhtml)
            #recipelink = '/apex/' + g.group(1)
                envobj.recipelink = recipelink
                logging.info("Recipelink: "+recipelink)
            else:
                logging.error("cannot find element: 'pInstance")
        else:
            logging.error("cannot find element: 'Run DataSet Recipe'")
            raise
        
    def getStatus(self):
        for env in self.envlist:
            envobj = Environment(env)
            self.__visitEnvPage(envobj)
            self.__getEnvStatus(envobj)
            if (envobj.status != "Running") and (envobj.status != "Requested"):
                self.__getEnvPass(envobj)
            self.__getExecStatus(envobj)
            self.__getOwners(envobj)
            self.envs[env] = envobj
    
    def __runClean(self, envobj):
        mUrl = self.__URL__ + envobj.recipelink
        logging.debug("Visiting recipe: %s" % mUrl)
        self.browser.visit(mUrl)
        if self.browser.is_element_present_by_xpath('//*[@id="B693598234623477311"]', 60):
            logging.debug("Selecting UCM Clean Environment Recipe")
            self.browser.choose('f01', '901')
            logging.debug("Starting Recipe")
            launchBtn = self.browser.find_by_xpath('//*[@id="B693598234623477311"]')
            launchBtn.click()
            if self.browser.is_element_present_by_xpath('//*[@id="B694724411644752651"]', 60): #confirmation button
                confLaunchBtn = self.browser.find_by_xpath('//*[@id="B694724411644752651"]')
                confLaunchBtn.click()
    
    def __retryClean(self, envobj):
        retrylink = self.browser.find_link_by_text("Retry Recipe Execution")
        retrylink.first.click()
        if self.browser.is_element_present_by_xpath('//*[@id="B453843285012723416"]', 60):
            confirmlink = self.browser.find_by_xpath('//*[@id="B453843285012723416"]')
            confirmlink.click()

    def __runPass(self, envobj):
        mUrl = self.__URL__ + envobj.recipelink
        logging.debug("Visiting recipe: %s" % mUrl)
        self.browser.visit(mUrl)
        if self.browser.is_element_present_by_xpath('//*[@id="B693598234623477311"]', 60):
            logging.debug("Selecting UCM - Passowrd Reset Recipe")
            self.browser.choose('f01', '1082')
            logging.debug("Starting Recipe")
            launchBtn = self.browser.find_by_xpath('//*[@id="B693598234623477311"]')
            launchBtn.click()
            if self.browser.is_element_present_by_xpath('//*[@id="B694724411644752651"]', 60): #confirmation button
                confLaunchBtn = self.browser.find_by_xpath('//*[@id="B694724411644752651"]')
                confLaunchBtn.click()
    
    def __retryPass(self, envobj):            # retry if in failed mode
        retrylink = self.browser.find_link_by_text("Retry Recipe Execution")
        retrylink.first.click()
        if self.browser.is_element_present_by_id("P15_RETRY_RECIPE_1",20):
            nolink = self.browser.find_by_id("P15_RETRY_RECIPE_1")
            nolink.click()
            if self.browser.is_element_present_by_id("P15_RECIPE_LIST", 10):
                reciperadio = self.browser.find_by_xpath("/html/body/form/div/div[2]/table/tbody/tr/td[1]/div[2]/div/section/div[2]/table[1]/tbody/tr[3]/td[2]/select/option[21]")
                reciperadio.click()
                #self.browser.choose('','1082')
                if self.browser.is_element_present_by_xpath('//*[@id="B453843285012723416"]', 60):
                    confirmlink = self.browser.find_by_xpath('//*[@id="B453843285012723416"]')
                    confirmlink.click()
    
    def envClean(self):                     # clean (ucm-all) environments
        logging.info("Clean mode selected")
        for env in self.envlist:
            logging.info("On env # "+env)
            envobj = Environment(env)
            self.__visitEnvPage(envobj)
            logging.info("EnvPage complete")
            self.__getEnvStatus(envobj)
            logging.info("EnvStatus complete")
            logging.info("Status: %s" % envobj.status)
            if envobj.status == "Completed" or envobj.status == "Cancelled":
                self.__getRecipeLink(envobj)
                logging.info("GetRecipeLink complete")
                self.__runClean(envobj)
                logging.info("runClean complete")
                envobj.modestatus = "clean"
            elif envobj.status == "Failed":
                self.__retryClean(envobj)
                logging.info("retryClean complete")
                envobj.modestatus = "clean"
            self.envs[env] = envobj
    
    def envPass(self):                      # reset password of environments
        for env in self.envlist:
            envobj = Environment(env)
            self.__visitEnvPage(envobj)
            self.__getEnvStatus(envobj)
            if envobj.status == "Completed":
                self.__getRecipeLink(envobj)
                self.__runPass(envobj)
                envobj.modestatus = "passwordreset"
            elif envobj.status == "Failed":
                self.__retryPass(envobj)
                envobj.modestatus = "passwordreset"
            self.envs[env] = envobj
    
    def prep(self):
        
        self.browser.visit(self.__URL__)    # visit main sit
        self.__login()                        # attempt login
        self.__getEnvLink()                   # get url for environments tab
        self.__getEnvBaseLink()               # get session info for environments
        logging.info("Prep Complete")
        
    def writeXls(self, mfile):              # write environments info to xls
        mxls = XLSModule(mfile, self.envs)
        mxls.process()

        
        
        