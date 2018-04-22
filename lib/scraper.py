'''
Created on Apr 3, 2018

@author: mkhan
'''
import time
import logging
import splinter
import re
from lib.xlsmodule import XLSModule

class Environment(object):
    
    def __init__(self, name):
        self.name = name
        self.password = ""
        self.status   = ""
        self.recipelink = ""
        self.esd = ""
        self.execet = ""
        self.execaet = ""
        self.owner = ""
        
    def __str__(self):
        mString = ""
        mString += "Name: " + self.name
        mString += "\nPassword: " + self.password
        mString += "\nOwner: " + self.owner
        mString += "\nStatus: " + self.status
        mString += "\nRecipe Link: " + self.recipelink
        mString += "\nRecipe Execution Start Date: " + self.esd
        mString += "\nRecipe Estimated Compl Time: " + self.execet
        mString += "\nRecipe Actual    Compl Time: " + self.execaet
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
        logging.debug(self.envlist)
        
        self.envs = {}
        
        Browser = splinter.Browser
        self.browser = Browser()    #default o
                
        logging.info("Initialized scraper...")
    
    def login(self):
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
        
        logging.info("Entering username")
        iUsername.fill(self.username)
        
        logging.info("Entering password")
        iPassword.fill(self.password)

        logging.info("Submitting")
        iSubmit.click()
    
    def getEnvLink(self):
        environments = []
        if self.browser.is_element_present_by_xpath('//*[@id="environments"]', 60):
            environments = self.browser.find_by_xpath('//*[@id="environments"]')
            env = environments[0]
            envhtml = env.outer_html
            p = re.compile('href=\"(.*)\"\s*id=')
            g = p.search(envhtml)
            self.envlink = g.group(1)
            self.browser.visit(self.__URL__ + self.envlink)
        else:
            logging.error("cannot find element: xpath: '//*[@id=\"environments\"]'")
            raise
        
    def getEnvBaseLink(self):
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
        else:
            logging.error("cannot find element: %s" % "/html/body/form/div/div/table/tbody/tr/td[1]/section/div[2]/div/table/tbody[3]/tr/td/table/tbody/tr/td[4]/a")
            raise
    
    def visitEnvPage(self, envobj):
        logging.info("Visiting Env: %s" % envobj.name)
        self.browser.visit(self.__URL__ + self.envbaselink + ":" +envobj.name)
        
    def getEnvPass(self, envobj):
        self.visitEnvPage(envobj)
        if self.browser.is_element_present_by_id("P15_RECIPE_STATUS", 60):
            envstatus = self.browser.find_by_id("P15_RECIPE_STATUS")
            if "Failed" in envstatus.value:
                envstatusval = "Failed"
            elif "Running" in envstatus.value:
                envstatusval = "Running"
            else:
                envstatusval = envstatus.value 
            envobj.status = envstatusval
            if (envobj.status == "Running"):
                return # dont get password
        if self.browser.is_element_present_by_id("P15_ENVIRONMENT_AAI_PASSWORD", 60):
            envpass = self.browser.find_by_id("P15_ENVIRONMENT_AAI_PASSWORD")
            envobj.password = envpass.text
            logging.info("Pass: %s" % envpass.text)
        else:
            logging.error("cannot find element: \"P15_ENVIRONMENT_AAI_PASSWORD\"")
            raise
        return envobj
    
    def getExecStatus(self, envobj):
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
        if envobj.status != "Completed": # live running env
            return
        if self.browser.is_element_present_by_text("Run DataSet Recipe", 60):
            recipeurl = self.browser.find_by_text("Run DataSet Recipe")
            recipeurlhtml = recipeurl.outer_html
            p = re.compile('href=\"(.*)\"\s*>')
            g = p.search(recipeurlhtml)
            recipelink = '/apex/' + g.group(1)
            envobj.recipelink = recipelink
        else:
            logging.error("cannot find element: 'Run DataSet Recipe'")
            raise
     
    def getOwner(self, envobj): 
        if self.browser.is_element_present_by_id("P15_PRIMARY_OWNER", 60):
            owner = self.browser.find_by_id("P15_PRIMARY_OWNER")
            envobj.owner = owner.text
        else:
            logging.error("cannot find element: \"P15_RECIPE_EXEC_ST_DISPLAY\"")
            raise
        
    def getStatus(self):
        for env in self.envlist:
            envobj = Environment(env)
            self.getEnvPass(envobj)
            self.getExecStatus(envobj)
            self.getOwner(envobj)
            self.envs[env] = envobj
    
    def runClean(self, envobj):
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
    
    def retryClean(self, envobj):
        retrylink = self.browser.find_link_by_text("Retry Recipe Execution")
        retrylink.first.click()
        if self.browser.is_element_present_by_xpath('//*[@id="B453843285012723416"]', 60):
            confirmlink = self.browser.find_by_xpath('//*[@id="B453843285012723416"]')
            confirmlink.click()

    def runPass(self, envobj):
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
    
    def retryPass(self, envobj):
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
    
    def envClean(self):
        for envname, envobj in self.envs.items():
            self.visitEnvPage(envobj)
            if envobj.status == "Completed":
                self.runClean(envobj)
            if envobj.status == "Failed":
                self.retryClean(envobj)
    
    def envPass(self):
        for envname, envobj in self.envs.items():
            self.visitEnvPage(envobj)
            if envobj.status == "Completed":
                self.runPass(envobj)
            if envobj.status == "Failed":
                self.retryPass(envobj)   
    
    def prep(self):
        self.browser.visit(self.__URL__)
        self.login()  
        self.getEnvLink()
        self.getEnvBaseLink()
        
    def writeXls(self, mfile):
        mxls = XLSModule(mfile, self.envs)
        mxls.process()

        
        
        