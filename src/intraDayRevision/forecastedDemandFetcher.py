import cx_Oracle
import pandas as pd
import datetime as dt
from typing import List, Tuple


class ForecastedDemandFetchRepo():
    """block wise forecasted demand fetch repository
    """

    def __init__(self, con_string):
        """initialize connection string
        Args:
            con_string ([type]): connection string 
        """
        self.connString = con_string


    def fetchForecastedDemand(self, startTime: dt.datetime, endTime: dt.datetime, entityTag:str) -> pd.core.frame.DataFrame:
        """fetch forecasted demand and return dataframe of it

        Args:
            startTime (dt.datetime): start time
            endTime (dt.datetime): end time
            entityTag (str): entity tag

        Returns:
            pd.core.frame.DataFrame: forecasted demand value of entity between startTime and endTime
        """  
        currdate = dt.datetime.now().replace(hour =0 ,minute =0,second=0, microsecond=0)
        startExceptionTime = currdate + dt.timedelta(hours = 22, minutes= 30) 
        endExceptionTime = currdate + dt.timedelta(hours = 22, minutes= 59) 

        if startExceptionTime <= dt.datetime.now() < endExceptionTime: 
            fetch_sql = "SELECT time_stamp, entity_tag, forecasted_demand_value FROM dfm3_forecast_revision_store WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') and entity_tag =:entity and revision_no='R0A' ORDER BY time_stamp"
           
        else:
            fetch_sql = "SELECT time_stamp, entity_tag, forecasted_demand_value FROM dfm3_dayahead_demand_forecast WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') and entity_tag =:entity ORDER BY time_stamp"       

        try:
            # connString=configDict['con_string_local']
            connection = cx_Oracle.connect(self.connString)

        except Exception as err:
            print('error while creating a connection', err)
        else:
            try:
                cur = connection.cursor()

                cur.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' ")
                forecastedDemandDf = pd.read_sql(fetch_sql, params={
                                 'start_time': startTime, 'end_time': endTime, 'entity':entityTag}, con=connection)

            except Exception as err:
                print('error while creating a cursor', err)
            else:
                connection.commit()
        finally:
            cur.close()
            connection.close()    

        return forecastedDemandDf

        