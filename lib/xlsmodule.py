'''
Created on Apr 19, 2018

@author: moe0277
@copyright: Copyright (C) Oracle Corporation

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
        self.__initWorkbook()
        
    def __initWorkbook(self):
        self.worksheet = self.workbook.add_worksheet()
        self.worksheet.set_landscape()
        self.worksheet.hide_gridlines(2)
        #self.worksheet.set_column(0,0, 10)
        self.worksheet.freeze_panes(1, 1)
        self.worksheet.set_column('A:G', 25)
        
        
        self.headerF = self.workbook.add_format({'bold': True})
        self.row = 0
        self.col = 0        
        self.merge_format = self.workbook.add_format({'bold':1, 'border':1, 'align':'center'})

        self.sumF = self.workbook.add_format({'bold': True})

    def __envRecord(self, envobj):  
        self.col = 0
        self.worksheet.write(self.row, self.col, envobj.name[4:])
        self.col += 1
        self.worksheet.write(self.row, self.col, envobj.password)
        self.col += 1
        self.worksheet.write(self.row, self.col, envobj.owner1)
        self.col += 1        
        self.worksheet.write(self.row, self.col, envobj.owner2)
        self.col += 1                
        self.worksheet.write(self.row, self.col, envobj.recipe)
        self.col += 1
        self.worksheet.write(self.row, self.col, envobj.status)
        self.col += 1
        self.worksheet.write(self.row, self.col, envobj.esd)
        self.col += 1
        self.worksheet.write(self.row, self.col, envobj.execaet)

    def __writeXlsHeaders(self):
        self.col = 0
        for header in self.headers:
            self.worksheet.write(self.row, self.col, header, self.headerF)    
            self.col += 1
                    
    def __initHeader(self):
        self.headers = ["Name","Password","Owner1","Owner2","Recipe","Status","Script Start","Script End"]
        self.__writeXlsHeaders()
        self.row += 1

    def process(self):
        self.__initHeader()
        for envname, envobj in self.envs.items():
            self.__envRecord(envobj)
            self.row += 1
        self.workbook.close()
        logging.debug("Wrote xls")
        