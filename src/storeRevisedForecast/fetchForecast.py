import cx_Oracle
import pandas as pd
import datetime as dt
from typing import List, Tuple


class RevisedForecastedDemandFetchRepo():
    """block wise revised forecasted demand fetch repository
    """

    def __init__(self, con_string):
        """initialize connection string
        Args:
            con_string ([type]): connection string 
        """
        self.connString = con_string
    
    def toListOfTuple(self, df:pd.core.frame.DataFrame) ->pd.core.frame.DataFrame:
        """convert forecasted BLOCKWISE demand data to list of tuples[(timestamp,entityTag,demandValue),]
        Args:
            df (pd.core.frame.DataFrame): forecasted block wise demand dataframe
        Returns:
            List[Tuple]: list of tuple of forecasted blockwise demand data [(timestamp,entityTag,demandValue),]
        """ 
        # df['revisionNo'] = 'R0'
        revisedDemandData:List[Tuple] = []
        
        for ind in df.index:
            demandTuple = (str(df['TIME_STAMP'][ind]), df['ENTITY_TAG'][ind], df['REVISION_NO'][ind], float(df['FORECASTED_DEMAND_VALUE'][ind]) )
            revisedDemandData.append(demandTuple)
            
        return revisedDemandData


    def fetchRevisedForecastedDemand(self, startTime: dt.datetime, endTime: dt.datetime, revisionNo:str) -> List[Tuple]:
        """fetch forecasted demand and return dataframe of it
        Args:
            startTime (dt.datetime): start time
            endTime (dt.datetime): end time
            revision no. (str): revision Number
        Returns:
            List[Tuple] : [(timestamp, entityTag, forecastedDemandValue),]
        """   
        #used only if R16 revision, that will be R0B revision for tomorrow     
        startTimeTomorrow = startTime + dt.timedelta(days=1)
        endTimeTomorrow = endTime + dt.timedelta(days=1)

        #list of tuple to store revised forecasted demand for today, and for tomorrow if revision Number is R16 
        revisedForecastedData : List[Tuple] =[]
        revisedForecastedDataR0B : List[Tuple] =[]

        try:
            # connString=configDict['con_string_local']
            connection = cx_Oracle.connect(self.connString)

        except Exception as err:
            print('error while creating a connection', err)
        else:
            
            try:
                cur = connection.cursor()
                fetch_sql = "SELECT time_stamp, entity_tag, forecasted_demand_value FROM dfm3_dayahead_demand_forecast WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') ORDER BY time_stamp"
                cur.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' ")
                forecastedDemandDf = pd.read_sql(fetch_sql, params={
                                 'start_time': startTime, 'end_time': endTime}, con=connection)
                forecastedDemandDf['REVISION_NO'] = revisionNo
                revisedForecastedData : List[Tuple] =self.toListOfTuple(forecastedDemandDf)
                
                #check for last revision, fetch tommorow forecast, add R0B to each tuple
                if revisionNo == 'R16':
                    fetch_sql = "SELECT time_stamp, entity_tag, forecasted_demand_value FROM dfm3_dayahead_demand_forecast WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') ORDER BY time_stamp"
                    # cur.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' ")
                    forecastedDemandDfR0B = pd.read_sql(fetch_sql, params={
                                    'start_time': startTimeTomorrow, 'end_time': endTimeTomorrow}, con=connection)
                    forecastedDemandDfR0B['REVISION_NO'] = 'R0B'
                    revisedForecastedDataR0B : List[Tuple] =self.toListOfTuple(forecastedDemandDfR0B)
                   
            except Exception as err:
                print('error while creating a cursor', err)
            else:
                connection.commit()
        finally:
            cur.close()
            connection.close()
        joinedForecastesData: List[Tuple] = [*revisedForecastedData, *revisedForecastedDataR0B]
        return joinedForecastesData