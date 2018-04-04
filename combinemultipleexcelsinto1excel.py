# -*- coding: utf-8 -*-
"""
Created on Tue Jun 06 13:05:31 2017

@author: BRS18
"""
# This is a python script to combine multiple excel files in similar format into a single excel to be used for analytic purposes

import pandas as pd
import glob

# filenames of the input excel files
path =r'file_path'
excel_names = glob.glob(path + "/*.xlsx")

# read them in
excels = [pd.ExcelFile(name) for name in excel_names]

# convert them into dataframes
framesEmp = [x.parse(x.sheet_names[0], header=None,index_col=None) for x in excels]
framesPerf = [x.parse(x.sheet_names[1], header=None,index_col=None) for x in excels]


# delete the first row for all frames except the first
# i.e. remove the header row -- assumes it's the first
framesEmp[1:] = [df[1:] for df in framesEmp[1:]]
framesPerf[1:] = [df[1:] for df in framesPerf[1:]]
# Formatted as per the requirement by concatenating them.
combinedEmp = pd.concat(framesEmp)
combinedPerf = pd.concat(framesPerf)
combinedEmp = combinedEmp.drop(combinedEmp.columns[[6,7,8,9,10,11,12]], axis=1)
combinedEmpnew = combinedEmp.dropna(axis=0, how='all')

# write the output to the desired excel file 
combinedEmpnew.to_excel('output_path', sheet_name='Sheet1', header=False, index=False)
combinedPerf.to_excel('output_path', sheet_name='Sheet1', header=False, index=False)


