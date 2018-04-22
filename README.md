# gsescraper notes

## Overview

gsecraper code connects to https://demo.oracle.com using a firefox driver 

## Pre-requisites

Python 3 (not tested with Python 2)  

Required python modules (use pip to install):  

1. splinter
2. xlsxwriter

## Launch instructions



## .ini file format

[common]  
;modes: status        = create xls w/ status (password, owner, and other information) of all envrionmements  
;modes: clean         = run the ucm clean all  script on all environments  
;modes: passwordreset = run the ucm password reset script on all environments  
mode=status  
;mode=clean  
;mode=passwordreset  
;username = oracle sso username
username=moe.f.khan@oracle.com
;password = oracle sso password  
password=xxxyyyzzz  
;comma separated list of environments (suggestion: test 1 environment initally to ensure it is working)
environments=ucm-gse000nnnnn,uvm-gse000nnnnn  

