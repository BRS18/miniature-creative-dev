# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 13:26:41 2021

@author: SarayuR
"""

import pandas as pd
import warnings
import numpy as np 
warnings.filterwarnings("ignore")


########## Creating master data on which all calculations will run ###########
##Function to find week number (1-52) and year so demand and supply can be aggregated. Also used to map with the inventory snapshot of the week.
def weekYear(DF, calendarDate):
    DF['weekNumber'] = DF[calendarDate].dt.isocalendar().week
    DF['year'] = DF[calendarDate].dt.isocalendar().year
    DF['weekYear'] = DF['year'].astype('str') +'_'+DF['weekNumber'].astype('str')
    return DF

##Function Sumifs - To calculate the sum of a certain column based on the given conditions. Similar to SUMIFS in excel.
def sumifs(summedDF,targetDF,keyColumns,sumColumn,targetColumnName,keyColumnLeft,keyColumnRight):
    summedDF =  summedDF.groupby(by=keyColumns)[sumColumn].agg('sum').reset_index()
    summedDF = summedDF.rename(columns={sumColumn[0]:targetColumnName})
    targetDF =   pd.merge(targetDF,summedDF,how = 'left',left_on=keyColumnLeft,right_on=keyColumnRight)
    return targetDF[targetColumnName]

##Function countifs - To calculate the count of a certain column based on the given conditions. Similar to COUNTIFS in excel.
def countifs(originalDF,keyColumns,targetColumn,targetDF,keyColumnLeft,keyColumnRight):
    originalDF = originalDF[keyColumns]
    originalDF[targetColumn] = 0
    countDF = originalDF.groupby(keyColumns)[targetColumn].agg('count').reset_index()
    targetDF =   pd.merge(targetDF,countDF,how = 'left',left_on=keyColumnLeft,right_on=keyColumnRight)
    targetDF[targetColumn] = targetDF[targetColumn].fillna(1)
    return targetDF[targetColumn]

##Function averageifs - To calculate the average of a certain column based on the given conditions. Similar to AVERAGEIFS in excel.
def averageifs(averageDF,targetDF,keyColumns,avgColumn,targetColumnName,keyColumnLeft,keyColumnRight):
    averageDF =  averageDF.groupby(by=keyColumns)[avgColumn].agg('mean').reset_index()
    averageDF = averageDF.rename(columns={avgColumn[0]:targetColumnName})
    targetDF =   pd.merge(targetDF,averageDF,how = 'left',left_on=keyColumnLeft,right_on=keyColumnRight)
    return targetDF[targetColumnName]

##Function to obtain sales order shipment data in the required format
def processDemand():
    salesorderDF = pd.read_csv(r"Inputdatalevel1/salesordershipment.csv",low_memory=False)
    salesorderDF['actualshippeddate'] = pd.to_datetime(salesorderDF["actualshippeddate"])
    salesorderDF = weekYear(salesorderDF, 'actualshippeddate')
    
    ##Finding how many days of data in each week is available.
    daysInWeek =  salesorderDF[['weekYear','actualshippeddate']]
    daysInWeek = daysInWeek.drop_duplicates()
    daysInWeek = daysInWeek.groupby(by=['weekYear']).count()
    daysInWeek = daysInWeek.reset_index()
    daysInWeek['nDays'] = daysInWeek['actualshippeddate']
    
    ##Removing weeks that has less than 6 days of data.
    salesorderDF = pd.merge(salesorderDF,daysInWeek,how='left',on=['weekYear'])
    salesorderDF = salesorderDF[salesorderDF['nDays']>=6]
    salesWeeklyDF = salesorderDF.groupby(by=['materialid','locationid','weekYear'])[['requestedquantity','shippedquantity']].agg('sum')
    salesWeeklyDF = salesWeeklyDF.reset_index()
    return salesWeeklyDF

##Function to obtain inventory history data in the required format
def processDemandInventory():
    inventoryhistoryDF = pd.read_csv(r"Inputdatalevel1/inventoryhistory.csv",low_memory=False)
    inventoryhistoryDF['snapshotdate'] = pd.to_datetime(inventoryhistoryDF["snapshotdate"])
    inventoryhistoryDF = weekYear(inventoryhistoryDF, 'snapshotdate')
    inventoryhistoryDF = inventoryhistoryDF[['materialid','locationid','transactionsubtype','quantity','weekYear']]
    inventoryhistoryDF['material_location'] = inventoryhistoryDF['materialid'].astype(str) + '_' + inventoryhistoryDF['locationid'].astype(str)

    inventoryUnrestricted = inventoryhistoryDF[inventoryhistoryDF['transactionsubtype']=='Unrestricted']
    inventoryUnrestricted = inventoryUnrestricted.rename(columns={'quantity':'quantityUnrestricted'})
    inventoryUnrestricted = inventoryUnrestricted[['materialid','locationid','weekYear','material_location','quantityUnrestricted']]
    return inventoryUnrestricted

##Obtaining manufacturing location data for a specific order or source location.
def getMaterialLocationMaster():
    materiallocationmstDF = pd.read_csv(r"Inputdatalevel1/materiallocationmst2.csv",low_memory=False)
    materiallocationmstDF['key'] = materiallocationmstDF['materialid'].astype('str')+'_'+materiallocationmstDF['locationid'].astype('str')
    #materiallocationmstDF = materiallocationmstDF.dropna(axis=1)
    return materiallocationmstDF

##Obtaining manufacturing location data for a specific order or source location.
def getManufacturingPlantLocation():
    manufacturingPlantDF = pd.read_csv(r"Inputdatalevel1/materialmaster.csv",low_memory=False)
    #manufacturingPlantDF['material_plant'] = manufacturingPlantDF['materialid'].astype('str')+'_'+manufacturingPlantDF['manufacturingplant'].astype('str')
    return manufacturingPlantDF

##Merging inventory data with demand data.
def mergeDemandInventory():
    inventoryUnrestricted = processDemandInventory()
    salesWeeklyDF = processDemand()
    materiallocationmstDF = getMaterialLocationMaster()
    manufacturingPlantDF = getManufacturingPlantLocation()
    inventoryUnrestricted = inventoryUnrestricted[['materialid','locationid','weekYear','quantityUnrestricted']]
    demand_inventory = pd.merge(salesWeeklyDF,inventoryUnrestricted,how='left',on=['materialid','locationid','weekYear'])
    demand_inventory['material_location'] = demand_inventory['materialid'].astype('str') +'_'+demand_inventory['locationid'].astype('str')
    demand_inventory = pd.merge(demand_inventory,materiallocationmstDF,how='left',on=['materialid','locationid'])
    demand_inventory = pd.merge(demand_inventory,manufacturingPlantDF,how='left',on=['materialid'])
    return demand_inventory