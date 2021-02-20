import pandas as pd
from typing import List, Tuple
import datetime as dt

def calculateRevisionwiseErrors(actualDemandDf:pd.core.frame.DataFrame, forecastedDemandDf:pd.core.frame.DataFrame, revisionNo:str, currDate:dt.date)->List[Tuple]:
    """calculate MAE, MAPE, RMSE, RMSE% and returns list of tuples

    Args:
        actualDemandDf (pd.core.frame.DataFrame):actual demand dataframe
        forecastedDemandDf (pd.core.frame.DataFrame):forecasted demand dataframe
        revisionNo (str): revision number
        currDate (dt.date):current date

    Returns:
        List[Tuple]: [(currDate, entity, revisionNo, mae, mape, rmse, rmsePercentage),]
    """    
    
    mwErrorDf = actualDemandDf 

    # calculating MAE, MAPE, RMSE, RMSE%
    mwErrorDf['absMwError'] = (actualDemandDf['DEMAND_VALUE']-forecastedDemandDf['FORECASTED_DEMAND_VALUE']).abs()
    mwErrorDf['abs%MwError'] = (((actualDemandDf['DEMAND_VALUE']-forecastedDemandDf['FORECASTED_DEMAND_VALUE'])/actualDemandDf['DEMAND_VALUE'])*100).abs()
    mwErrorDf['squaredMwError'] = (mwErrorDf['absMwError']*mwErrorDf['absMwError'])
    mwErrorDf['squared%MwError'] = (mwErrorDf['abs%MwError']*mwErrorDf['abs%MwError'])

    data:List[Tuple] =[]

    groupe=mwErrorDf.groupby("ENTITY_TAG")
    for entity,groupDf in groupe:
        mae = groupDf['absMwError'].mean()
        mape = groupDf['abs%MwError'].mean()
        rmse = (groupDf['squaredMwError'].mean())**(1/2)
        rmsePercentage = (groupDf['squared%MwError'].mean())**(1/2)
        tupleStore = (currDate, entity, revisionNo, mae, mape, rmse, rmsePercentage)
        data.append(tupleStore)
    
    return data


    

    

    
    