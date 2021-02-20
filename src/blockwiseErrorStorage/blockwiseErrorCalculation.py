import pandas as pd
from typing import List, Tuple

def calculateMwError(actualDemandDf:pd.core.frame.DataFrame, forecastedDemandDf:pd.core.frame.DataFrame, revisionNo:str)->List[Tuple]:
    """calculate mw & percentage mw error and return 

    Args:
        actualDemandDf (pd.core.frame.DataFrame): actual demand dataframe
        forecastedDemandDf (pd.core.frame.DataFrame): forecasted demand dataframe
        revisionNo (str): revision number

    Returns:
        List[Tuple]: [(TIME_STAMP, ENTITY_TAG, revsionNo, mwError, %mwError)]
    """    
    mwErrorDf = actualDemandDf 
    mwErrorDf['mwError'] = (actualDemandDf['DEMAND_VALUE'] - forecastedDemandDf['FORECASTED_DEMAND_VALUE'])
    mwErrorDf['%mwError'] = ((actualDemandDf['DEMAND_VALUE']-forecastedDemandDf['FORECASTED_DEMAND_VALUE'])/actualDemandDf['DEMAND_VALUE'])*100
    mwErrorDf['revisionNo'] = revisionNo

    data:List[Tuple] =[]
    for ind in mwErrorDf.index:
        rowTuple = (str(mwErrorDf['TIME_STAMP'][ind]), mwErrorDf['ENTITY_TAG'][ind], mwErrorDf['revisionNo'][ind], float(mwErrorDf['mwError'][ind]), float(mwErrorDf['%mwError'][ind]) )
        data.append(rowTuple)
    return data
