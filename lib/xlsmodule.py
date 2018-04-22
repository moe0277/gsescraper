'''
Created on Apr 19, 2018

@author: mkhan01
'''

import xlsxwriter
import logging

class XLSModule(object):
    '''
    classdocs
    '''

    def __init__(self, mFile, envs):
        '''
        Constructor
        '''
        self.envs = envs
        self.file = mFile
        self.workbook = xlsxwriter.Workbook(self.file)
        self.initWorkbook()
        
    def initWorkbook(self):
        self.worksheet = self.workbook.add_worksheet()
        self.worksheet.set_landscape()
        self.worksheet.hide_gridlines(2)
        #self.worksheet.set_column(0,0, 10)
        self.worksheet.freeze_panes(1, 1)
        self.worksheet.set_column('A:F', 25)
        
        
        self.headerF = self.workbook.add_format({'bold': True})
#        self.headerF.set_rotation(90)
        self.row = 0
        self.col = 0        
        self.merge_format = self.workbook.add_format({'bold':1, 'border':1, 'align':'center'})

        self.sumF = self.workbook.add_format({'bold': True})

    def writeXlsHeaders(self):
        self.col = 0
        for header in self.headers:
            self.worksheet.write(self.row, self.col, header, self.headerF)    
            self.col += 1
    
    def envRecord(self, envobj):  
        self.col = 0
        self.worksheet.write(self.row, self.col, envobj.name)
        self.col += 1
        self.worksheet.write(self.row, self.col, envobj.password)
        self.col += 1
        self.worksheet.write(self.row, self.col, envobj.owner)
        self.col += 1        
        self.worksheet.write(self.row, self.col, envobj.status)
        self.col += 1
        self.worksheet.write(self.row, self.col, envobj.esd)
        self.col += 1
        self.worksheet.write(self.row, self.col, envobj.execaet)
                
    def initHeader(self):
        self.headers = ["Name","Password","Owner","Status","Script Start","Script End"]
        self.writeXlsHeaders()
        self.row += 1

    def process(self):
        self.initHeader()
        for envname, envobj in self.envs.items():
            self.envRecord(envobj)
            self.row += 1
        self.workbook.close()
        logging.debug("Wrote xls")
        