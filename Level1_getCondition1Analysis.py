# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 13:50:17 2021

@author: SarayuR
"""

import numpy as np
import pandas as pd 
import warnings
warnings.filterwarnings("ignore")

from Level1_getInputData import weekYear,sumifs,countifs,averageifs,processDemand,processDemandInventory,getMaterialLocationMaster,mergeDemandInventory

##Function to obtain demand inventory data and add the necessary calculated columns for Level 1 Analysis
def getInventoryHealth(demand_inventory_fromMain):
    demand_inventory = demand_inventory_fromMain 
    demand_inventory.rename(columns={"inventoryucl": "maxTarget", "inventorylcl": "minTarget"}, inplace = True)
    demand_inventory['health'] = np.where(demand_inventory['quantityUnrestricted'] < demand_inventory['minTarget'],"Shortage",
                                          np.where(demand_inventory['quantityUnrestricted'] > demand_inventory['maxTarget'],"Excess","Healthy"))
    demand_inventory['inventoryValue'] = demand_inventory['cogsperunit'] * demand_inventory['quantityUnrestricted']
    demand_inventory['averageDailyDemandValue1'] = sumifs(summedDF = demand_inventory,
                                                                                         targetDF = demand_inventory,
                                                                                         keyColumns = ['material_location'],
                                                                                         sumColumn = ['requestedquantity'],
                                                                                         targetColumnName = 'averageDailyDemandValue1',
                                                                                         keyColumnLeft = ['material_location'],
                                                                                         keyColumnRight = ['material_location'])
    demand_inventory['averageDailyDemandValue2'] = countifs(originalDF=demand_inventory,
                                                                        keyColumns=['material_location'],
                                                                        targetColumn='averageDailyDemandValue2',
                                                                        targetDF=demand_inventory,
                                                                        keyColumnLeft = ['material_location'],
                                                                        keyColumnRight = ['material_location'])
    
    demand_inventory['averageDailyDemand'] = (demand_inventory['averageDailyDemandValue1']/ demand_inventory['averageDailyDemandValue2'])/7
    demand_inventory['averageDailyDemandValue'] =  demand_inventory['averageDailyDemand'] * demand_inventory['cogsperunit'] 
    demand_inventory.drop(columns=['averageDailyDemandValue1','averageDailyDemandValue2'],inplace=True)
    demand_inventory['averageInventory'] = averageifs(averageDF = demand_inventory,
                                                                                         targetDF = demand_inventory,
                                                                                         keyColumns = ['materialid','locationid'],
                                                                                         avgColumn = ['quantityUnrestricted'],
                                                                                         targetColumnName = 'averageInventory',
                                                                                         keyColumnLeft = ['materialid','locationid'],
                                                                                         keyColumnRight = ['materialid','locationid'])
    demand_inventory['averageInventoryValue'] =  demand_inventory['cogsperunit'] *  demand_inventory['averageInventory'] 
    demand_inventory['inventoryDays'] = demand_inventory['averageInventoryValue'] / demand_inventory['averageDailyDemandValue'] 
    demand_inventory = demand_inventory.sort_values('averageDailyDemandValue', ascending=False)
    demand_inventory['cummulativeAverageDailyDemandValue'] = np.cumsum(demand_inventory['averageDailyDemandValue'])
    demand_inventory['percentCumsum'] = (demand_inventory['cummulativeAverageDailyDemandValue']) / (demand_inventory['averageDailyDemandValue'].sum())
    demand_inventory['ABC'] = np.where(demand_inventory['percentCumsum'] <= 0.8,"A",
                                       np.where(demand_inventory['percentCumsum'] <= 0.9 , "B","C"))
    demand_inventory['daysBucket'] = np.where(demand_inventory['inventoryDays'] < 15, "0-15",
                                              np.where((demand_inventory['inventoryDays'] > 15) & (demand_inventory['inventoryDays'] < 30) , "15-30",
                                                       np.where((demand_inventory['inventoryDays'] > 30) & (demand_inventory['inventoryDays'] < 45),"30-45",
                                                                np.where((demand_inventory['inventoryDays'] > 45) & (demand_inventory['inventoryDays'] < 60),"45-60", "60+"))))
    return demand_inventory

##Function to obtain Purchase Orders Data and add the necessary calculated columns
def getPurchaseOrders():
    ##Obtaining purchase orders data for a specific order.
    purchaseOrderDF = pd.read_csv(r"Inputdatalevel1/PurchaseOrders.csv",low_memory=False)
    purchaseOrderDF.fillna(0)
    purchaseOrderDF['otifFlag'] = np.where((purchaseOrderDF['DeliveredQuantity'] >= purchaseOrderDF['RequestedQuantity']) & (purchaseOrderDF['ActualReceiptDate'] <= purchaseOrderDF['RequestedReceiptDate']), 1,0)
    purchaseOrderDF['casesOTIF'] = purchaseOrderDF['otifFlag'] * purchaseOrderDF['RequestedQuantity']
    return purchaseOrderDF
    