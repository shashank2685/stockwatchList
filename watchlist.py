#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from Tkinter import *
from tkintertable.Tables import TableCanvas
from tkintertable.TableModels import TableModel
import ystockquote
import re


class Rows():
    def __init__(self, result, symbol):
        columns = Columns()
        self.row = { columns.getColumns()[0] : symbol}
        cols = columns.getColumns()
        for index in range(1, columns.getlength()):
            if columns.getMapping(cols[index]) in result:
                if cols[index] == "Last Price":
                    res = re.findall("[0-9.]+" , result[columns.getMapping(cols[index])])
                    self.row[cols[index]] = res[-1]
                else:
                    self.row[cols[index]] = result[columns.getMapping(cols[index])]
                if cols[index] == "%Change":
                    res = re.sub("\"", " ", result[columns.getMapping(cols[index])])
                    self.row[cols[index]] = res
            else:
                self.row[cols[index]] = "No Data"

    def getRow(self):
        return self.row

    def getValue(self,symbol):
        if symbol in self.row:
            return self.row.get(symbol, None)
        else:
            return "N/A"

class Columns():
    def __init__(self):
        self.columns = ['Symbol','Last Price', 'Change', '%Change',
                        #'Prev Close', 'Bid', 'Ask'
                        ]
        self.mapping = {'Last Price' : 'last_trade_price', 
                        'Change' : 'change', 
                        '%Change' : 'change_percent',
                        #'Prev Close' : 'previous_close', 
                        #'Bid' : 'bid_realtime', 
                        #'Ask' : 'ask_realtime'
                        }
        self.columnDict = { 'columnorder' : { 1 : 'Symbol', 2 : 'Last Price', 3 : 'Change', 4 : '%Change'
                                            #, 5 : 'Prev Close', 6 : 'Bid', 7 : 'Ask'
                                            },
                            'columnlabels' : {'Symbol' : 'Symbol', 'Last Price':'Last Price', 'Change':'Change','%Change':'%Change'
                                            #,'Prev Close':'Prev Close','Bid' : 'Bid','Ask':'Ask'
                                            },
                            'columntypes' :  {'Symbol' : 'text', 'Last Price':'text','Change':'text','%Change':'text'
                                            #,'Prev Close':'text','Bid':'text','Ask':'text'
                                            } }

    def getColumns(self):
        return self.columns

    def getlength(self):
        return len(self.columns)

    def getMapping(self, column):
        if column in self.mapping:
            return self.mapping.get(column, None)
        else:
            return "N/A"

    def getColumnsDict(self) :
        return self.columnDict

class Watchlist(Tk):

    def __init__(self,parent):
        Tk.__init__(self,parent)
        self.parent = parent
        self.currentRow = 1
        self.rows = []
        self.Objcolumn = Columns()
        self.initialize()
        

    def addStock(self, args=None):
        stockSym = self.sysmTextIn.get()
        if stockSym == None:
            return
        else :
            self.addRow(stockSym)
            return

    def addRow(self, stockSym):
        self.sysmTextIn.delete(0, END)
        searchterms = [('Symbol', stockSym.upper(), '=', 'AND')]
        symbolCol = self.model.getColumnData(columnIndex=self.model.getColumnIndex(columnName="Symbol"),
                                             columnName="Symbol", filters=searchterms)
        if stockSym.upper() in symbolCol:
            return
        result = ystockquote.get_all(stockSym.upper())

        row = Rows(result, stockSym.upper())
        dictrow = row.getRow()
        colIndex = self.model.getColumnIndex(columnName="Symbol")
        stockSym = self.model.getValueAt(rowIndex=0, columnIndex=colIndex)
        if stockSym == " ":
            row0 = self.table.getSelectedRow()
            self.model.deleteRow(row0)
            self.table.setSelectedRow(row0-1)
            self.table.clearSelected()
        else:
            self.currentRow = self.currentRow + 1
        self.model.importDict({ "%s%d" % ("rec", self.currentRow) : dictrow})
        change = float(dictrow['Change'])
        if change > 0:
            self.model.setColorAt(rowIndex=self.model.getRecordIndex("%s%d" % ("rec", self.currentRow)),
                                  columnIndex=self.model.getColumnIndex(columnName="Change"),color="green", key="fg") 
            self.model.setColorAt(rowIndex=self.model.getRecordIndex("%s%d" % ("rec", self.currentRow)),
                                  columnIndex=self.model.getColumnIndex(columnName="%Change"),color="green", key="fg")
        if change < 0:
            self.model.setColorAt(rowIndex=self.model.getRecordIndex("%s%d" % ("rec", self.currentRow)),
                                  columnIndex=self.model.getColumnIndex(columnName="Change"),color="red", key="fg") 
            self.model.setColorAt(rowIndex=self.model.getRecordIndex("%s%d" % ("rec", self.currentRow)),
                                  columnIndex=self.model.getColumnIndex(columnName="%Change"),color="red", key="fg")
        self.table.redrawTable()
        self.after(5000, self.updateTableValue, "%s%d" % ("rec", self.currentRow))
        
    def fadeIn(self, rec) :
        if rec not in self.model.data:
            return
        self.model.setColorAt(rowIndex=self.model.getRecordIndex(rec),
                              columnIndex=self.model.getColumnIndex(columnName="Last Price"),color="white")
        self.table.redrawTable()
                

    def updateTableValue(self, rec):
        increased = False
        decreased = False
        
        if rec not in self.model.data:
            return
        
        result = ystockquote.get_all(self.model.data[rec]['Symbol'].upper())
        row = Rows(result, self.model.data[rec]['Symbol'].upper())
        dictrow = row.getRow()
        change = float(dictrow['Change'])
        #print "update table value" + self.model.data[rec]['Symbol'].upper()
        if change > 0:
            self.model.setColorAt(rowIndex=self.model.getRecordIndex(rec),
                                  columnIndex=self.model.getColumnIndex(columnName="Change"),color="green", key="fg") 
            self.model.setColorAt(rowIndex=self.model.getRecordIndex(rec),
                                  columnIndex=self.model.getColumnIndex(columnName="%Change"),color="green", key="fg")
        if change < 0:
            self.model.setColorAt(rowIndex=self.model.getRecordIndex(rec),
                                  columnIndex=self.model.getColumnIndex(columnName="Change"),color="red", key="fg") 
            self.model.setColorAt(rowIndex=self.model.getRecordIndex(rec),
                                  columnIndex=self.model.getColumnIndex(columnName="%Change"),color="red", key="fg")
        if float(self.model.data[rec]['Last Price']) > float(dictrow['Last Price']):
            color="Red"
            decreased = True
        if float(self.model.data[rec]['Last Price']) < float(dictrow['Last Price']):
                color="Green"
                increased = True
        if (decreased == True) or (increased == True):
            self.model.setColorAt(rowIndex=self.model.getRecordIndex(rec),
                                  columnIndex=self.model.getColumnIndex(columnName="Last Price"),color=color) 
            for col in self.model.data[rec]:
                self.model.data[rec][col] = dictrow[col]
        self.table.redrawTable()
        self.id = self.after(5000, self.updateTableValue, rec)
        self.id = self.after(1000, self.fadeIn, rec)

                    
                    

                
    def initialize(self):
        mainframe = Frame(self,padx=3, pady=12)
        mainframe.grid(column=0, row=0, sticky=(N,E,W,S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.minsize(400, 400)


        subframe = Frame(mainframe)
        subframe.grid(row=0, column=0, sticky="NW")
        label = Label(subframe, text="Stock Symbol : ")
        label.pack(side="left")
        
        mainframe.symTextIn = Entry(subframe)
        self.sysmTextIn = mainframe.symTextIn
        self.sysmTextIn.bind("<Return>", self.addStock)
        mainframe.symTextIn.pack(side="left")

        addButton = Button(subframe,text=u"Add", command=self.addStock)
        addButton.pack(side="left", pady=5, padx=5)

        blueRow = Label(mainframe,fg="white",bg="blue")
        blueRow.grid(column=0,row=1,columnspan=3,sticky=(E,W))
        mainframe.columnconfigure(0, weight=1)

        self.tableframe = Frame(mainframe, height=200, width=200, background="black")
        self.tableframe.grid(column=0, row=2,columnspan=3, sticky=(N,E,W,S))
        mainframe.rowconfigure(2, weight=1)
        mainframe.columnconfigure(0, weight=1)
        
        mainframe.bind("<Return>", self.addStock)
        self.sysmTextIn.focus()
        #Create column Headers.
        self.model = TableModel(newdict=self.Objcolumn.getColumnsDict())
        self.table = TableCanvas(self.tableframe, model=self.model, cols=len(self.Objcolumn.getColumns()),thefont=('Arial',9),
                                rowheight=18, cellwidth=80, editable=False, selectedcolor='white', rowselectedcolor='white',
                                autoresizecols=0, inset=0, width=350)
        self.model.importDict({'rec0' : {'Symbol' : ' ', 'Last Price':' ',
                               'Change':' ','%Change':' '
                               #,'Prev Close':' ','Bid':' ','Ask':' '
                               }})
        self.table.createTableFrame()
        self.table.redrawTable()
        

    
if __name__ == "__main__":
    app = Watchlist(None)
    app.title('Watchlist')
    app.mainloop()
