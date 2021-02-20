import pandas as pd
import datetime as dt
from typing import List, Tuple, TypedDict
from src.fetchers.scadaApiFetcher import ScadaApiFetcher

def toMinuteWiseData(demandDf:pd.core.frame.DataFrame, entity:str)->pd.core.frame.DataFrame:
    """convert random secondwise demand dataframe to minwise demand dataframe and add entity column to dataframe.

    Args:
        demandDf (pd.core.frame.DataFrame): random secondwise demand dataframe
        entity (str): entity name

    Returns:
        pd.core.frame.DataFrame: minwise demand dataframe
    """    
    try:
        demandDf = demandDf.resample('1min', on='timestamp').agg({'demandValue': 'first'})  # this will set timestamp as index of dataframe
    except Exception as err:
        print('error while resampling', err)
    demandDf.insert(0, "entityTag", entity)                      # inserting column entityName with all values of 96 block = entity
    demandDf.reset_index(inplace=True)
    return demandDf

def filterAction(demandDf :pd.core.frame.DataFrame, minRamp:int)-> pd.core.frame.DataFrame:
    """ apply filtering action 

    Args:
        demandDf (pd.core.frame.DataFrame): unfiltered demand df
        minRamp (int): threshold deviation value for min-min ramping

    Returns:
        filtered dataframe
    """    
    for ind in demandDf.index.tolist()[1:]:
        if abs(demandDf['demandValue'][ind]-demandDf['demandValue'][ind-1]) > minRamp :
            demandDf['demandValue'][ind] = demandDf['demandValue'][ind-1]
    return demandDf
            
def applyFilteringToDf(demandDf:pd.core.frame.DataFrame, entity:str) -> pd.core.frame.DataFrame:
    """applying filtering logic

    Args:
        demandDf (pd.core.frame.DataFrame): unfiltered demand dataframe
        entity (str): entityTag

    Returns:
        pd.core.frame.DataFrame: filtered demand dataframe
    """    
    #500,200,1000,2000 are min to min ramp of entities 
    if entity == 'WRLDCMP.SCADA1.A0046945':
        filteredDemandDf = filterAction(demandDf, 500)

    if entity == 'WRLDCMP.SCADA1.A0046948' or entity == 'WRLDCMP.SCADA1.A0046962' or entity == 'WRLDCMP.SCADA1.A0046953':
        filteredDemandDf = filterAction(demandDf, 200)
    
    if entity == 'WRLDCMP.SCADA1.A0046957' or entity == 'WRLDCMP.SCADA1.A0046978' or entity == 'WRLDCMP.SCADA1.A0046980':
        filteredDemandDf = filterAction(demandDf, 1000)
   
    if entity == 'WRLDCMP.SCADA1.A0047000':
        filteredDemandDf = filterAction(demandDf, 2000)
    return filteredDemandDf

def toBlockwiseDemand(minwiseDemandDf: pd.core.frame.DataFrame, entityTag:str) ->pd.core.frame.DataFrame :
        """convert minute wise demand data to block wise deamnd data
        Args:
            minwiseDemandDf (pd.core.frame.DataFrame): minute wise demand dataframe
        Returns:
            pd.core.frame.DataFrame: block wise demand dataframe
        """        
        try:
            blockwiseDemandDf = minwiseDemandDf.resample('15min', on='timestamp').mean()   # this will set timestamp as index of dataframe
        except Exception as err:
            print('error while resampling', err)
        blockwiseDemandDf.insert(0, "entityTag", entityTag)                      # inserting column entityName with all values of 96 block = entity
        blockwiseDemandDf.reset_index(inplace=True)
        return blockwiseDemandDf

def fetchDemandDataFromApi(startTime: dt.datetime,endTime: dt.datetime, entityTag:str, configDict: dict)->pd.core.frame.DataFrame :
    """fetch demand data from api for a particular entity and returns dataframe

    Args:
        startTime (dt.datetime): startTime
        endTime (dt.datetime): endTime
        entityTag (str): entityTag
        configDict (dict): application configuration

    Returns:
        pd.core.frame.DataFrame: return actual demand dataframe
    """    
      
    tokenUrl: str = configDict['tokenUrl']
    apiBaseUrl: str = configDict['apiBaseUrl']
    clientId = configDict['clientId']
    clientSecret = configDict['clientSecret']
    
    #creating object of ScadaApiFetcher class 
    obj_scadaApiFetcher = ScadaApiFetcher(tokenUrl, apiBaseUrl, clientId, clientSecret)

    # fetching secondwise data from api for each entity(timestamp,value) and converting to dataframe
    resData = obj_scadaApiFetcher.fetchData(entityTag, startTime, startTime)
    demandDf = pd.DataFrame(resData, columns =['timestamp','demandValue']) 

    #filtering for 6 blocks only
    demandDf = demandDf[(demandDf['timestamp'] >= startTime) & (demandDf['timestamp'] <= endTime)]

    #converting to minutewise data and adding entityName column to dataframe
    demandDf = toMinuteWiseData(demandDf,entityTag)
    
    #handling missing values NANs
    demandDf['demandValue'].fillna(method='ffill', inplace= True)
    demandDf['demandValue'].fillna(method='bfill', inplace= True)

    #applying filtering logic
    filteredDemandDf = applyFilteringToDf(demandDf,entityTag)

    # resampling to blockwise demand
    blockwiseDf = toBlockwiseDemand(filteredDemandDf,entityTag)

    return blockwiseDf
    

