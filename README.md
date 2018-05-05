# gsescraper

## Overview

gsecraper automates operations on demo.oracle.com.  

It connects to https://demo.oracle.com using a firefox driver.  

It supports 3 modes:  

1. **status**: scrapes the password, status, and other values for environments specified in the .ini file. 
1. **clean**: runs the UCM Clean All recipe against the envrionments specified. 
1. **passwordreset**: (DEPRECATED) runs the UCM Password reset recipe against the environments specified.  

For the **status** mode, it also generates a *gsescraper.xlsx* file containing the results of the status scrape. 

### Typical operation

1. Run *gsescraper* in **status mode**. Review the status of the environments in *gsescraper.xlsx*. 
1. Run *gsescraper* in **clean mode**. **NOTE:** you must have ownership of the environment(s) in order to run recipes. 
1. Run *gsescraper* in (DEPRECATED) **passwordreset** mode if needed (normally, clean recipe will reset passwords as well) and this mode is not required. 

The **clean**, and **passwordreset** modes can run against environments in both *Completed* and *Failed* states. 
 
## Pre-requisites

Python 3 (not tested with Python 2)    
Only tested on Windows; should work on Mac OSX w/ modifications. 

Required python modules (use pip to install):  

1. splinter
2. xlsxwriter

## Run instructions

1. Create a *gsescraper.ini* file, for template see below or the *gsescraper.ini.sample* file.
1. If mode=**status**, ensure *gsescraper.xslsx* is not open / in use. 
1. Using Python 3, start *gsescraper.py* (launch from the same directory as rest of the codebase).
1. During execution, do not interfere with the automated firefox window. However, you can work on other windows. 
1. If mode=**status**, at the end of the execution - a new *gsescraper.xlsx* will be created. 
1. If needed, review the *gsescraper.py.log* file for runtime log. 

## .ini file format

[common]  
;mode 
;status        create xls w/ status (password, owner, and other information) of all envrionmements  
;clean         run the ucm clean all  script on all environments  
;passwordreset (DEPRECATED) run the ucm password reset script on all environments  
mode=status  
;mode=clean  
;mode=passwordreset  
;username = oracle sso username  
username=moe.f.khan@oracle.com  
;password = oracle sso password  
password=xxxyyyzzz  
;environments comma separated list of environments (suggestion: test 1 environment initally to ensure it is working)  
environments=ucm-gse000nnnnn,uvm-gse000nnnnn  
