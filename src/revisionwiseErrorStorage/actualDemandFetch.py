import cx_Oracle
import pandas as pd
import datetime as dt
from typing import List, Tuple, TypedDict


class ActualDemandFetchRepo():
    """fetch actual demand data for a day 
    """

    def __init__(self, con_string):
        """initialize connection string
        Args:
            con_string ([type]): connection string 
        """
        self.connString = con_string

    def fetchActualDemand(self, startDate:dt.datetime, endDate:dt.datetime) ->pd.core.frame.DataFrame:
        """fetch actual demand of a day

        Args:
            startDate (dt.datetime): start date
            endDate (dt.datetime): end date

        Returns:
            pd.core.frame.DataFrame: dataframe that contains actual demand
        """    

        start_time_value = startDate
        end_time_value = endDate + dt.timedelta(hours=23, minutes= 59)
        try:
            
            connection = cx_Oracle.connect(self.connString)

        except Exception as err:
            print('error while creating a connection', err)
        else:
            
            try:
                cur = connection.cursor()
                fetch_sql = "SELECT time_stamp, entity_tag, demand_value FROM interpolated_blockwise_demand WHERE time_stamp BETWEEN TO_DATE(:start_time,'YYYY-MM-DD HH24:MI:SS') and TO_DATE(:end_time,'YYYY-MM-DD HH24:MI:SS') ORDER BY entity_tag, time_stamp"
                cur.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS' ")
                blockwiseDemandDf = pd.read_sql(fetch_sql, params={
                                 'start_time': start_time_value, 'end_time': end_time_value}, con=connection)

            except Exception as err:
                print('error while creating a cursor', err)
            else:
                connection.commit()
        finally:
            cur.close()
            connection.close()
        return blockwiseDemandDf