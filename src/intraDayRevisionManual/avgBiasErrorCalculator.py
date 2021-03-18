import pandas as pd
def calculateAvgBiasError(actualDemandDf:pd.core.frame.DataFrame, forecastedDemandDf:pd.core.frame.DataFrame)->float:
    """calculate avg bias error of last six blocks and retrun avg bias error

    Args:
        actualDemandDf (pd.core.frame.DataFrame): actual demand dataframe
        forecastedDemandDf (pd.core.frame.DataFrame): forecasted demand dataframe

    Returns:
        float: avg bias error
    """    
    biasErrorDf=pd.DataFrame() 
    biasErrorDf['biasError'] = (actualDemandDf['demandValue']-forecastedDemandDf['FORECASTED_DEMAND_VALUE'])/actualDemandDf['demandValue']
    avgBiasError = biasErrorDf['biasError'].mean()
    return avgBiasError
    