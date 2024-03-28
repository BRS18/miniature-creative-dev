# -*- coding: utf-8 -*-
"""
Created on Wed Dec  8 13:31:39 2021

@author: SarayuR
"""

import warnings
warnings.filterwarnings("ignore")
from Level1_getInputData import weekYear,sumifs,countifs,processDemand,processDemandInventory,getMaterialLocationMaster,mergeDemandInventory
from Level1_getCondition1Analysis import getInventoryHealth,getPurchaseOrders

##Main funtion to call the other functions in a necessary order
def main():
   demand_inventory =  mergeDemandInventory()
   demand_inventory = demand_inventory.dropna(axis='columns')
   demand_inventory = getInventoryHealth(demand_inventory)
   purchase_orders = getPurchaseOrders()
   
   ##Output to CSV files
   #demand_inventory.to_csv(r'C:\Users\SarayuR\OneDrive - USEReady Technology Private Limited\My Work\McKinsey\SC Insights\Level1Analysis\Level1AnalyisFinalOutput.csv',index=False)
   #purchase_orders.to_csv(r'C:\Users\SarayuR\OneDrive - USEReady Technology Private Limited\My Work\McKinsey\SC Insights\Level1Analysis\PurchaseOrdersFinalOutput.csv',index=False)
   
   print("Execution is Completed")
   
if __name__== "__main__" :
    main()