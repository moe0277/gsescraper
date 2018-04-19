'''
Created on Apr 3, 2018

@author: mkhan
'''
import time
import logging
import splinter
import re


class GSEScraper(object):
    '''
    classdocs
    '''

    __URL__ = "https://demo.oracle.com/" 

    def __init__(self, username, password, envs):
        '''
        Constructor
        '''
        self.username = username
        self.password = password
        self.envs = envs
        self.envhash = {}
        
        Browser = splinter.Browser
        #elf.browser = Browser('chrome')
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
    
    def environments(self):
        count = 0
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
        
    def getEnvBase(self):
        initialEnv = self.envs[0]
 
        environments = []
        #if self.browser.is_element_present_by_id(initialEnv, 60):
        if self.browser.is_element_present_by_xpath("/html/body/form/div/div/table/tbody/tr/td[1]/section/div[2]/div/table/tbody[3]/tr/td/table/tbody/tr/td[4]/a", 60): #the next link i.e. pagination
            environments = self.browser.find_link_by_partial_text("ucm-gse")
            
            #environments = self.browser.find_by_id(initialEnv)
            env = environments[0]
            envhtml = env.outer_html
            p = re.compile('href=\"(.*)\"\s*title=')
            g = p.search(envhtml)
            envbaseraw = '/apex/' + g.group(1)
            envbases = envbaseraw.split(":")
            s = ":"
            self.envbase = s.join(envbases[:-1])
            #self.browser.visit(self.__URL__ + self.envbase)
        else:
            logging.error("cannot find element: %s" % initialEnv)
            raise
    
    def visitenvpage(self, env):
        logging.info("Visiting Env: %s" % env)
        self.browser.visit(self.__URL__ + self.envbase + ":" +env)
        
    def getenvpass(self, env):
        self.visitenvpage(env)
        if self.browser.is_element_present_by_id("P15_RECIPE_STATUS", 60):
            envstatus = self.browser.find_by_id("P15_RECIPE_STATUS")
            self.envhash[env] = {"status": envstatus.value}
            if self.envhash[env]["status"] != "Completed":
                return # dont get password
        if self.browser.is_element_present_by_id("P15_ENVIRONMENT_AAI_PASSWORD", 60):
            envpass = self.browser.find_by_id("P15_ENVIRONMENT_AAI_PASSWORD")
            self.envhash[env]["pass"] = envpass.text
            logging.info("Pass: %s" % envpass.text)
        else:
            logging.error("cannot find element: \"P15_ENVIRONMENT_AAI_PASSWORD\"")
            raise
        
    def getexecstatus(self, env):
        if self.browser.is_element_present_by_id("P15_RECIPE_EXEC_ST_DISPLAY", 60):
            esd = self.browser.find_by_id("P15_RECIPE_EXEC_ST_DISPLAY")
            self.envhash[env]['esd'] = esd.text
        else:
            logging.error("cannot find element: \"P15_RECIPE_EXEC_ST_DISPLAY\"")
            raise
        if self.browser.is_element_present_by_id("P15_RECIPE_EXEC_ET_DISPLAY", 60):
            execet = self.browser.find_by_id("P15_RECIPE_EXEC_ET_DISPLAY")
            self.envhash[env]['execet'] = execet.text
        else:
            logging.error("cannot find element: \"P15_RECIPE_EXEC_ET_DISPLAY\"")
            raise
        if self.browser.is_element_present_by_id("P15_RECIPE_EXEC_A_ET_DISPLAY",60):
            execaet = self.browser.find_by_id("P15_RECIPE_EXEC_A_ET_DISPLAY")
            self.envhash[env]['execaet'] = execaet.text
        else:
            logging.error("cannot find element: \"P15_RECIPE_EXEC_A_ET_DISPLAY\"")
            raise
        if self.envhash[env]['status'] != "Completed": # live running env
            return
        if self.browser.is_element_present_by_text("Run DataSet Recipe", 60):
            recipeurl = self.browser.find_by_text("Run DataSet Recipe")
            recipeurlhtml = recipeurl.outer_html
            p = re.compile('href=\"(.*)\"\s*>')
            g = p.search(recipeurlhtml)
            recipelink = '/apex/' + g.group(1)
            self.envhash[env]['recipelink'] = recipelink
        else:
            logging.error("cannot find element: 'Run DataSet Recipe'")
            raise
        
            
    def getstatus(self):
        for env in self.envs:
            self.getenvpass(env)
            self.getexecstatus(env)
    
    def runclean(self, env):
        murl = self.__URL__ + self.envhash[env]['recipelink']
        logging.debug("Visitng recipe: %s" % murl)
        self.browser.visit(murl)
        if self.browser.is_element_present_by_xpath('//*[@id="B693598234623477311"]', 60):
            logging.debug("Selecting UCM Clean Environment Recipe")
            self.browser.choose('f01', '901')
            logging.debug("Starting Recipe")
            launchbtn = self.browser.find_by_xpath('//*[@id="B693598234623477311"]')
            launchbtn.click()
            if self.browser.is_element_present_by_xpath('//*[@id="B694724411644752651"]', 60): #confirmation button
                conflaunchbtn = self.browser.find_by_xpath('//*[@id="B694724411644752651"]')
                conflaunchbtn.click()
            
        
        
    
    def envclean(self, env):
        self.visitenvpage(env)
        self.runclean(env)
    
    def prep(self):
        self.browser.visit(self.__URL__)
        self.login()  
        self.environments()
        self.getEnvBase()

        
        
        