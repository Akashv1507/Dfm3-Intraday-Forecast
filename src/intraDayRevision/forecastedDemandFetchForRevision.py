import cx_Oracle
import pandas as pd
import datetime as dt
from typing import List, Tuple


class ForecastedDemandFetchForRevisionRepo():
    """block wise forecasted demand fetch repository
    """

    def __init__(self, con_string):
        """initialize connection string
        Args:
            con_string ([type]): connection string 
        """
        self.connString = con_string
    
    def toListOfTuple(self,df:pd.core.frame.DataFrame) -> List[Tuple]:
        """convert forecasted BLOCKWISE demand data to list of tuples[(timestamp,entityTag,demandValue),]
        Args:
            df (pd.core.frame.DataFrame): forecasted block wise demand dataframe
        Returns:
            List[Tuple]: list of tuple of forecasted blockwise demand data [(timestamp,entityTag,demandValue),]
        """ 
        demandData =[]
        for ind in df.index:
            demandTuple = (str(df['TIME_STAMP'][ind]), df['ENTITY_TAG'][ind], float(df['FORECASTED_DEMAND_VALUE'][ind]) )
            demandData.append(demandTuple)
        return demandData


    def fetchForecastedDemandForRevision(self, start_Time: dt.datetime, end_Time: dt.datetime, entityTag:str, avgBiasError: float) -> List[Tuple]:
        """fetch forecasted demand from B+3 blocks, applying DA R0 forecast*(1+avg forecast bias error), and return list of tuple [(timestamp,entityTag,demandValue),]

        Args:
            startTime (dt.datetime): start time
            endTime (dt.datetime): end time
            entityTag (str): entity tag
            avgBiasError(float): calculated avg bias error

        Returns:
            List[Tuple]:  list of tuple [(timestamp,entityTag,demandValue),]
        """
        # startTime = b+3 block        
        startTime = end_Time + dt.timedelta(minutes= 46)

        #endTime will today last block if not in 22:30 - 22:45 revision block else tommorows last block 
        currdate = dt.datetime.now().replace(hour =0 ,minute =0,second=0, microsecond=0)
        # currdate = dt.datetime.strptime("2021-01-29 12:10:40", '%Y-%m-%d %H:%M:%S').replace(hour =0 ,minute =0,second=0, microsecond=0)
        startExceptionTime = currdate + dt.timedelta(hours = 22, minutes= 30) 
        endExceptionTime = currdate + dt.timedelta(hours = 22, minutes= 45) 

        if startExceptionTime <= dt.datetime.now() < endExceptionTime:
        # if startExceptionTime <= dt.datetime.strptime("2021-01-29 12:10:40", '%Y-%m-%d %H:%M:%S') < endExceptionTime:
            endTime = currdate + dt.timedelta(days=1, hours=23, minutes=59)
            fetch_sql = "SELECT time_stamp, entity_tag, forecasted_demand_value FROM dfm3_forecast_revision_store WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') and entity_tag =:entity and revision_no='R0A' ORDER BY time_stamp"

        else:
            endTime = currdate + dt.timedelta(hours=23, minutes=59)
            fetch_sql = "SELECT time_stamp, entity_tag, forecasted_demand_value FROM dfm3_dayahead_demand_forecast WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') and entity_tag =:entity ORDER BY time_stamp"

        try: 
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

        #applying DA R0 forecast*(1+avg forecast bias error)
        
        forecastedDemandDf['FORECASTED_DEMAND_VALUE'] = forecastedDemandDf['FORECASTED_DEMAND_VALUE']*(1+avgBiasError)
        
        data : List[Tuple] = self.toListOfTuple(forecastedDemandDf)
        return data